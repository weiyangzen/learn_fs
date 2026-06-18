# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/host_sve.c

Purpose: this selftest checks host FPSIMD/SVE/SME state save/restore across repeated `KVM_RUN` ioctls. It focuses on host context preservation rather than guest SVE support.

Important APIs and functions: guest `guest_code()` emits ten `GUEST_UCALL_NONE()` exits and then `GUEST_DONE()`. Host functions include `handle_sigill()`, `register_sigill_handler()`, `do_sve_roundtrip()`, `test_run()`, and `main()`. Inline assembly sets predicate register `p0`, counts active bits before and after a recoverable `udf #0`, and compares counts.

Control flow: `main()` checks `AT_HWCAP` for `HWCAP_SVE` and skips if absent. `test_run()` registers a SIGILL handler, creates a one-vCPU VM, tests SVE state once, then runs the vCPU loop. Each guest `UCALL_NONE` triggers two host SVE roundtrips before the next `KVM_RUN`.

State and persistence: no durable state. Host signal context is modified to skip the `udf` instruction by advancing PC. SVE predicate state is transient and tested across signal and KVM transitions.

Dependencies and integration points: depends on host SVE hardware support, signal handling, inline SVE assembly, libkvm VM creation, and ucall handling.

Risks: the inline assembly requires SVE-capable compiler/toolchain support. The test assumes SIGILL recovery from `udf #0` and that predicate register `p0` can be clobbered/observed as written. It does not validate guest SVE exposure.

Test signals: printed before/after predicate counts should match for every signal/KVM roundtrip. Mismatch calls `TEST_FAIL`; lack of SVE returns `KSFT_SKIP`.
