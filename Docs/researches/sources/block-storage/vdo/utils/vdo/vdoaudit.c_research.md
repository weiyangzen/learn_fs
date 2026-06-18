# File Research: sources/block-storage/vdo/utils/vdo/vdoaudit.c

## Purpose

`vdoaudit.c` implements `vdoAudit`, a consistency checker for an offline VDO backing device. It audits:

- Logical block count from block map entries versus saved recovery journal count.
- Block map entry validity.
- Physical block reference counts observed from the block map versus stored slab reference counts.
- Slab summary free-space hints versus actual free blocks.

It can print either summary output or verbose per-error diagnostics.

## Command-Line Interface

Usage:

```text
vdoAudit [ [--summary] | [--verbose] ] <filename>
```

Options:

- `--help`
- `--summary`
- `--verbose`
- `--version`

`--summary` is the default behavior.

## Key Data Structures

`SlabAudit` tracks audit state for each slab:

- `slabNumber`
- `slabOrigin`
- `refCounts`: audited reference counts derived from block map traversal.
- `badRefCounts`
- `deltaCounts`: histogram of stored minus audited reference deltas.
- `firstError`
- `lastError`

Global audit state includes:

- `vdo`
- `slabSummaryEntries`
- `slabDataBlocks`
- `hintShift`
- `lbnCount`
- `slabs[MAX_VDO_SLABS]`
- `badBlockMappings`
- `badRefCounts`
- `badSlabs`
- `badSummaryHints`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Loads VDO read-only with `makeVDOFromFile()`.
4. Initializes one `SlabAudit` per slab and allocates each slab’s `refCounts`.
5. Calls `auditVDO()`.
6. Prints success message or summary.
7. Frees allocations and exits `0` on pass, `1` otherwise.

`auditVDO()`:

1. Rejects `VDO_NEW` as unauditable.
2. Warns if VDO state is not `VDO_CLEAN`.
3. Calls `examineBlockMapEntries(vdo, examineBlockMapEntry)` to validate mappings and populate audited refs.
4. Loads slab summary with `readSlabSummary()`.
5. Compares counted logical blocks with `vdo->states.recovery_journal.logical_blocks_used`.
6. Calls `verifyPBNRefCounts()`.
7. Returns success only if logical count, ref counts, and summary hints all match.

## Block Map Auditing

`examineBlockMapEntry()` validates each mapping:

- Unmapped entries must use `VDO_ZERO_BLOCK`.
- Compressed states must not point at `VDO_ZERO_BLOCK`.
- Leaf mappings increment `lbnCount`.
- PBNs must map to a valid slab and data block, not slab metadata.
- Interior tree page references are marked as `PROVISIONAL_REFERENCE_COUNT`.
- Duplicate interior tree page references, compressed tree pages, or refcount overflows are reported as mapping problems.

## Reference Count Auditing

`verifyPBNRefCounts()` allocates a buffer for slab reference count metadata and calls `verifySlab()` for each slab.

`verifySlab()`:

- For pristine slabs where `load_ref_counts` is false, expects all audited references to be zero and all slab data blocks to be free.
- For used slabs, reads reference count blocks from disk and compares them to audited references.

`verifyRefCountSector()` handles special provisional values:

- Tree pages may validly have stored reference count `1` or `MAXIMUM_REFERENCE_COUNT`.
- Empty audited refs with stored `PROVISIONAL_REFERENCE_COUNT` are tolerated.

`verifySummaryHint()` checks slab free block count against `fullness_hint << hintShift` with an allowed error of `1 << hintShift`.

## Output

Verbose mode uses `warnx()` for detailed mapping/refcount/summary issues.

Summary mode prints:

- Total block mapping errors.
- Total free-space hint errors.
- Total reference count errors.
- Total slabs containing errors.
- Per-slab error range and histogram.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `linux/fs.h`, `stdio.h`, `stdlib.h`, `sys/ioctl.h`, `sys/stat.h`, `unistd.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `memory-alloc.h`, `syscalls.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO user helpers: `blockMapUtils.h`, `slabSummaryReader.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `slabs` is statically sized to `MAX_VDO_SLABS`, matching VDO constraints.
- `freeAuditAllocations()` assumes `vdo` is non-null when iterating `vdo->slabCount`; current call sites satisfy this after VDO loading.
- Summary warnings for a clean logical block count are printed with `warnx()`, so success diagnostics go to stderr.
- The auditor can continue after some per-entry mapping problems, but hard errors from traversal or reads cause audit failure.
