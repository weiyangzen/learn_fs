# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pid-vm.c

Purpose: x86_64 procfs VM layout test using a hand-built one-page ELF whose process unmaps all other VMAs. It validates `/proc/$pid/maps`, `smaps`, `smaps_rollup`, `statm`, and `PROCMAP_QUERY` against precise expectations.

Important APIs and functions: `make_private_tmp()` creates an isolated tmpfs; `make_exe()` builds an ET_EXEC ELF in an `O_TMPFILE`; `vsyscall()` detects amd64 vsyscall mode; raw payload code performs `munmap`, writes a pipe byte, then pauses. The parent uses `execveat(AT_EMPTY_PATH)`, `stat`, proc file reads, `memmem`, and `ioctl(PROCMAP_QUERY)`.

Control flow: setup private mount namespace and tmpfs, reserve fd 0 for child synchronization, create the tiny executable, fork/exec it, wait for the payload byte after unmapping, synthesize expected `/proc/$pid/maps` line from tmpfs device/inode, then verify all proc VM interfaces and ioctl query cases.

State and persistence: temporary executable exists only by fd and appears as deleted tmpfs path in maps. Global `pid` is killed by an `atexit` handler if still live.

Dependencies and integration: requires x86_64, tmpfs, mount namespace permission, `execveat`, proc page monitor files, and kernel headers containing `struct procmap_query`.

Risks and test signals: exact string formatting and fixed `MAPS_OFFSET` make the test sensitive to proc output format changes. Failures identify regressions in single-VMA accounting, deleted file names, vsyscall reporting, or procmap query matching and filtering.
