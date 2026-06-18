<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h

## Purpose
`relocs.h` is the shared interface for the x86 relocation extraction host tool.

## Important APIs, types, and functions
It defines `enum symtype`, `ARRAY_SIZE`, the `die()` printf/noreturn declaration, and `process_32()`/`process_64()` prototypes with flags for realmode, text output, absolute-symbol reporting, and relocation info.

## Control flow
`relocs_common.c` parses CLI/options and dispatches to `process_32` or `process_64`; `relocs_32.c` and `relocs_64.c` include the common implementation with ELF-width macros.

## State and persistence behavior
No runtime kernel state exists; the header standardizes process-local parsing state across translation units.

## Dependencies and integration points
It depends on libc, ELF headers, endian helpers, regex, and `tools/le_byteshift.h`.

## Risks and edge cases
ABI mismatches between this header and `relocs.c` wrappers can produce wrong ELF class handling. Host endianness support is intentionally explicit.

## Test signals
Signals are clean host-tool compilation and relocation output for both 32-bit, 64-bit, and `--realmode` ELF files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h -->
