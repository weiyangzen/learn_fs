<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h

## Purpose
Public interface and usage notes for the vDSO parser.

## Important APIs, Types, and Functions
vdso_sym, vdso_init_from_sysinfo_ehdr prototypes.

## Control Flow
Documents the call sequence: initialize from AT_SYSINFO_EHDR, then resolve symbol names and versions.

## State and Persistence
No state in the header; implementation state lives in parse_vdso.c.

## Dependencies and Integration Points
Included by all vDSO tests that need symbol lookup.

## Risks and Edge Cases
Consumers must cache vdso_sym results and avoid racing init.

## Test Signals
Compile-time integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h -->
