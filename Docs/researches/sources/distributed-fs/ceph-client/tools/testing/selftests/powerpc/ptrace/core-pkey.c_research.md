# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/core-pkey.c

## Purpose
`core-pkey.c` verifies that POWER protection-key registers are written into ELF core notes correctly. It drives a child to set AMR/IAMR/UAMOR values, forces a core dump, and inspects the resulting core file.

## Important APIs, Types, and Functions
Important routines are `increase_core_file_limit()`, `child()`, `try_core_file()`, `next_note()`, `check_core_file()`, `parent()`, `write_core_pattern()`, `setup_core_pattern()`, `core_pkey()`, and `main()`. `struct shared_info` carries synchronization and expected pkey register values.

## Control Flow and State
The test raises the core size limit, optionally adjusts `/proc/sys/kernel/core_pattern`, creates shared memory, forks, has the child allocate pkeys and update pkey registers, then crashes to produce a core. The parent waits, mmaps the core file, scans ELF notes for pkey register data, compares AMR/IAMR/UAMOR values, and restores core_pattern if changed. Persistent external state is limited to core_pattern and generated core files; both are cleaned/restored by the test path.

## Dependencies and Integration Points
It integrates ptrace/pkey helpers, ELF note parsing, SysV shared memory, `/proc/sys/kernel/core_pattern`, resource limits, and kernel core-dump pkey note support.

## Risks and Test Signals
Risks include insufficient privilege to change core_pattern, small core limits, stale core files, note layout changes, and pkey allocation failure. A pass means core notes preserve the pkey registers established by the child.
