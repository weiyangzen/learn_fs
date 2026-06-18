<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c

Purpose: Validates execute permission behavior for anonymous memory on radix-capable powerpc systems. It ensures non-executable mappings fault and executable mappings run.

Important APIs and types: Defines PPC instruction constants, `is_fault_expected`, SIGTRAP/SIGSEGV handlers, `check_exec_fault(int rights)`, `test()`, and `main()`.

Control flow: `test()` skips without POWER9/radix-era capability, maps one page writable, fills it with NOPs and a final BLR, then exercises read/write/execute combinations through `mprotect`. Fault handlers restore permissions so each case can continue.

State and persistence: Global `fault_code`, `remaining_faults`, `fault_addr`, `pgsize`, and instruction buffer track the active case. No persistent state is written.

Dependencies and integration points: Depends on `pkeys.h` for helpers/HWCAP checks, POSIX signals, `mprotect`, and the powerpc instruction set.

Risks: Expected fault codes differ when pkeys are enabled, so the helper accepts `SEGV_PKUERR` only when pkeys are supported. Signal handler recovery must stay async-signal-safe enough for test use.

Test signals: Pass confirms read/write/execute permission separation and expected fault reporting for executable anonymous pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c -->
