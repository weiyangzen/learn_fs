# File Research: sources/block-storage/vdo/utils/vdo/vdoStatsWriter.c

## Purpose

`vdoStatsWriter.c` formats an in-memory `struct vdo_statistics` into a verbose, aligned text report. It is the writer half used by `vdostats.c` when verbose/YAML-like output is requested after `read_vdo_stats()` has decoded the kernel/device-mapper stats message.

The top comment says new statistics must be kept in sync with:

- `../base/statistics.h`
- `../base/message-stats.c`
- `../base/pool-sysfs-stats.c`
- `./messageStatsReader.c`
- `../../../perl/Permabit/Statistics/Definitions.pm`

## Main Data Flow

The file keeps global output state:

- `fieldCount`: number of label/value rows currently populated.
- `maxLabelLength`: longest label for alignment.
- `labels[MAX_STATS][MAX_STAT_LENGTH]`
- `values[MAX_STATS][MAX_STAT_LENGTH]`

`vdo_write_stats(struct vdo_statistics *stats)` resets those globals, calls `write_vdo_statistics(" ", stats)`, then prints all collected rows as:

```text
<label><padding> : <value>
```

## Core Helpers

Primitive writers:

- `write_u8()`
- `write_u64()`
- `write_string()`
- `write_block_count_t()`
- `write_u32()`
- `write_double()`

Each writes a label string to `labels[fieldCount]`, updates `maxLabelLength`, writes the formatted value to `values[fieldCount]`, then increments `fieldCount`.

Nested statistics writers:

- `write_block_allocator_statistics()`
- `write_commit_statistics()`
- `write_recovery_journal_statistics()`
- `write_packer_statistics()`
- `write_slab_journal_statistics()`
- `write_slab_summary_statistics()`
- `write_ref_counts_statistics()`
- `write_block_map_statistics()`
- `write_hash_lock_statistics()`
- `write_error_statistics()`
- `write_bio_stats()`
- `write_memory_usage()`
- `write_index_statistics()`
- `write_vdo_statistics()`

These build labels with `asprintf()`, pass nested field values to primitive writers, free the temporary label, and propagate any non-`VDO_SUCCESS` result.

## Important Calculations

`write_vdo_statistics()` derives several user-facing values:

- `one_k_blocks = physical_blocks * block_size / 1024`
- `one_k_blocks_used = (data_blocks_used + overhead_blocks_used) * block_size / 1024`
- `one_k_blocks_available = (physical_blocks - data_blocks_used - overhead_blocks_used) * block_size / 1024`
- `used_percent` rounded to nearest integer.
- `saving_percent`, based on logical blocks used versus physical data blocks used.
- `512 byte emulation` string based on `logical_block_size == 512`.
- `write_amplification_ratio` from `(bios_meta.write + bios_out.write) / bios_in.write`, rounded with `roundf()` and later printed with two decimals.

Several capacity and savings fields are emitted as `"N/A"` when the VDO is in recovery mode or when `stats->mode` is `"read-only"`.

## Dependencies

Includes:

- Generic C: `stdio.h`, `stdlib.h`, `string.h`
- Utility headers: `numeric.h`, `string-utils.h`
- VDO/base headers: `math.h`, `statistics.h`, `status-codes.h`, `types.h`, `vdoStats.h`

The file depends heavily on the layout of `struct vdo_statistics` and its nested structs.

## Notable Behaviors and Risks

- `MAX_STATS` is fixed at `239`. If the stats schema grows without updating this constant, the primitive writers can write past `labels`/`values`.
- `MAX_STAT_LENGTH` is fixed at `80`, but labels are written with `sprintf()` rather than bounded `snprintf()`. Current labels appear intended to fit, but this is a schema-coupled safety assumption.
- All label construction uses `asprintf()` and frees correctly after use.
- `write_double()` prints with `%.2f`, but `write_amplification_ratio` is already rounded to an integer-valued float via `roundf()`, so the display loses fractional ratio precision.
- The leading prefix passed from `vdo_write_stats()` is `" "`, so all labels intentionally begin with a leading space.
