<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c

## Purpose
Reference ELF parser used by vDSO tests to initialize from AT_SYSINFO_EHDR and resolve versioned symbols.

## Important APIs, Types, and Functions
vdso_init_from_sysinfo_ehdr, vdso_sym, elf_hash, gnu_hash, vdso_match_version, check_sym, static vdso_info.

## Control Flow
Parses ELF headers/program headers, computes load offset, extracts dynamic string/symbol/hash/version tables, supports GNU hash and SysV hash lookup, and returns function addresses for matching name/version symbols.

## State and Persistence
Maintains one static global vdso_info cache; init is not thread-safe while vdso_sym is read-only after initialization.

## Dependencies and Integration Points
Depends on ELF layout, auxv-provided vDSO base, parse_vdso.h, and architecture ELF_BITS selection.

## Risks and Edge Cases
Malformed or unexpected vDSO tables can make lookup fail; version matching linearly scans verdef and assumes standard table consistency.

## Test Signals
Tests using vdso_sym skip when symbols are absent and fail when resolved calls behave incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c -->
