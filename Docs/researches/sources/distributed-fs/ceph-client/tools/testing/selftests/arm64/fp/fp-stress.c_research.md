<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c

Purpose: orchestrates a stress run of multiple FP/vector child tests across CPUs and vector lengths, while periodically injecting signals. It exercises context switching, signal save/restore, preemption, and kernel FP users concurrently.

Important APIs and functions: uses `fork`, `pipe`, `dup2`, `execl`, `epoll`, `waitpid`, `SIGCHLD`, `SIGUSR1`, `SIGTERM`, `prctl(PR_SVE_SET_VL/PR_SME_SET_VL)`, and `getauxval`. Core functions are `child_start`, `child_output_read`, `child_output`, `child_tickle`, `child_stop`, `child_cleanup`, `start_fpsimd`, `start_kernel`, `start_sve`, `start_ssve`, `start_za`, `start_zt`, `probe_vls`, and `drain_output`.

Control flow: parse `--timeout`, count CPUs, probe SVE/SME VLs, schedule FPSIMD and kernel tests for every CPU plus SVE/SSVE/ZA per supported VL and ZT for SME2. Children wait on a shared startup pipe until all have forked. The parent reads child stdout with epoll, waits until all children emitted startup output, then periodically sends SIGUSR1 until timeout or termination, sends SIGTERM, drains output, waits, and reports per-child TAP results.

State and persistence: in-memory `children` table tracks PID, stdout pipe, partial output, and exit status. No persistent files; child output is streamed through kselftest logs.

Dependencies and integration: runs sibling binaries `fpsimd-test`, `kernel-test`, `sve-test`, `ssve-test`, `za-test`, and `zt-test`; depends on HWCAP feature bits and prctl VL inheritance so execed children start with intended VLs.

Risks: high process counts scale with CPUs and VLs. Startup detection depends on each child printing output. Signal and epoll handling must avoid losing child output or leaving live processes on failure.

Test signals: kselftest plan equals scheduled child count; success requires each child to produce output and exit with status 0 after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c -->
