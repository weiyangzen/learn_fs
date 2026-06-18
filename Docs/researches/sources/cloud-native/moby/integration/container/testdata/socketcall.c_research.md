# sources/cloud-native/moby/integration/container/testdata/socketcall.c

Purpose: C fixture for testing the ia32 `socketcall(2)` compatibility path from an amd64 process, especially where seccomp cannot inspect socket arguments behind a userspace pointer.

Important APIs and flow: Compile-time macros `SOCK_FAMILY` and `SOCK_TYPE` choose the socket parameters. The program allocates an argument array below 4 GB with `mmap(... MAP_32BIT ...)`, invokes `int $0x80` with syscall number 102 and operation `SYS_SOCKET`, converts negative returns to `errno`, and reports success or `perror("socket")`.

State and dependencies: It uses one low-address mmap region and closes the socket on success. It depends on x86-compatible inline assembly, Linux syscall ABI, and compiler macro injection from the test.

Risks and signals: It exercises a subtle bypass surface: seccomp argument filtering cannot see the family through `socketcall`, so LSM enforcement must deny AF_ALG while allowing AF_INET. Fixture changes could weaken that security signal.
