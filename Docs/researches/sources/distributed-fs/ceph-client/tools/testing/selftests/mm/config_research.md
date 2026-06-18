# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/config

Purpose: kernel config fragment for broad mm selftest coverage.

Important APIs/types/functions: requests SysV IPC, userfaultfd and PTE markers, test vmalloc/HMM/GUP modules, THP, soft-dirty, anon VMA names, tracing/profiling/uprobe support, memory failure/hwpoison injection, and forced `/proc/pid/mem` behavior.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: supports many tests built by `mm/Makefile`, including COW, GUP, THP, HMM, vmalloc, and memory failure cases.

Risks: this fragment is not exhaustive for every optional runtime path; external libraries and hardware still affect coverage.

Test signals: configured kernels expose the features required by most mm selftests.
