<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c

## Purpose
`gen-devlist.c` is a host-side build tool that transforms the Zorro ID database into C macro invocations consumed by `names.c`.

## Important APIs, types, and functions
The program uses `main` and helper `pq` for quote escaping. It emits `MANUF`, `PRODUCT`, and `ENDMANUF` records to `devlist.h`.

## Control flow
It reads `zorro.ids` from stdin, skips blank/comment lines, parses manufacturer lines and tab-indented product lines, validates name lengths, truncates bracketed product descriptions if needed, escapes quotes, and closes the last manufacturer block.

## State and persistence
State is parser-local: current manufacturer ID/name length, mode, line number, and output file handle. Persistent output is generated `devlist.h`.

## Dependencies and integration points
It depends on stdio/string libc and the exact text format of `zorro.ids`. `names.c` includes the generated header multiple times with different macro definitions.

## Risks and test signals
Risks include fixed-size manufacturer buffers, strict whitespace assumptions, overlong names, malformed IDs, and stale generated output. Test signals include generator execution in kbuild, malformed fixture lines, quote escaping, long descriptions, and empty database handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c -->
