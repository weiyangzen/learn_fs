<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c

## Purpose
`relocs_common.c` contains the CLI front end for the `relocs` host tool and dispatches to 32-bit or 64-bit ELF processors.

## Important APIs, types, and functions
Important functions are `die()`, `usage()`, and `main()`. Options include `--abs-syms`, `--abs-relocs`, `--reloc-info`, `--text`, and `--realmode`.

## Control flow
`main()` parses options, opens the ELF file, reads `e_ident`, rewinds, chooses `process_64()` for `ELFCLASS64` or `process_32()` otherwise, and closes the file.

## State and persistence behavior
State is option flags, filename, file pointer, and the ELF identification buffer. It writes relocation data or diagnostics to standard output/error.

## Dependencies and integration points
It depends on `relocs.h`, libc file I/O, and the specialized processors compiled from `relocs_32.c`/`relocs_64.c`.

## Risks and edge cases
An unreadable or malformed file aborts the build. Dispatch is based only on `EI_CLASS`; detailed machine/type validation happens later.

## Test signals
Signals are CLI usage checks, realmode relocation generation, absolute-relocation audits, and kbuild invocations from realmode/compressed kernel rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c -->
