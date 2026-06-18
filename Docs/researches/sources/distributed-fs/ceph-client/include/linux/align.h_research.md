<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/align.h -->
# sources/distributed-fs/ceph-client/include/linux/align.h

## Purpose
`align.h` is a Linux include wrapper around generic vDSO alignment helpers.

## Important APIs, types, and functions
It includes `<vdso/align.h>` and defines no local macros or functions. Consumers receive the alignment macros/types exported by the vDSO header.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is created. The file affects compile-time macro availability only.

## Dependencies and integration points
It provides a stable Linux include path for code that needs alignment helpers shared with vDSO code.

## Risks and test signals
Risks are limited to include-path breakage and wrapper/header guard mismatch. Test signals are header self-containment builds and users of `ALIGN`-style helpers through this include.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/align.h -->
