<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S

Purpose: assembly SME2 ZT0 context-switch and signal-restore stress test.

Important APIs and symbols: helpers `pattern`, `setup_zt`, `memcmp`, `check_zt`, signal handlers, `setsignal`, `barf`, and `svcr_barf`; `_start` drives execution. Uses `smstart_za`, `_ldr_zt`, `_str_zt`, raw syscalls, and SVCR reads.

Control flow: install handlers, enable ZA, get PID, then loop by generation. Each iteration fills ZT0 and shadow memory, yields, verifies SVCR has ZA=1/SM=0, stores ZT0 to scratch, compares against shadow, and repeats. SIGUSR1 resets SME state; signal return should restore interrupted state.

State and persistence: `.data` contains `ztref` and `scratch` sized to 512 bits. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, and `sme-inst.h`; run by `fp-stress` on SME2 systems.

Risks: only tests ZT0, consistent with current SME2 ZT regset size. Requires SME2 instruction support and accurate signal context restoration.

Test signals: startup prints PID; mismatch dumps expected/actual ZT bytes and SVCR; clean SIGTERM reports iterations and signal count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S -->
