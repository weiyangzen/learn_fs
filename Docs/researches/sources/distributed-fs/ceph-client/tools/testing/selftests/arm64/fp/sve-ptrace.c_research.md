<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c

Purpose: ptrace ABI selftest for SVE and streaming SVE regsets, including unsupported behavior, VL setting, inherit flags, FPSIMD-format access, and SVE/FPSIMD data conversion.

Important APIs, types, and functions: `struct vec_type` describes SVE and streaming SVE regset metadata. Helpers include `do_child`, `get_fpsimd`, `set_fpsimd`, `get_sve`, `set_sve`, `read_fails`, `write_fails`, `ptrace_set_get_inherit`, `ptrace_set_get_vl`, `ptrace_set_vl_ranges`, `ptrace_sve_fpsimd`, `ptrace_sve_fpsimd_no_sve`, `ptrace_set_sve_get_sve_data`, `ptrace_set_sve_get_fpsimd_data`, `ptrace_set_fpsimd_get_sve_data`, and `do_parent`.

Control flow: child calls `PTRACE_TRACEME` and stops. Parent waits for the specific SIGSTOP, then for each vector type checks unsupported reads/writes, FPSIMD-format writes through SVE regset, inherit flag set/clear, invalid VL rejection, every candidate VQ up to `TEST_VQ_MAX`, and data round-trips for supported VLs. SME-only systems also test FPSIMD writes through NT_ARM_SVE despite no SVE hardware.

State and persistence: dynamic buffers hold variable-size `user_sve_header` payloads. No disk persistence. Random data is generated with `random()`.

Dependencies and integration: uses Linux arm64 ptrace regsets, `asm/sigcontext.h`, `asm/ptrace.h`, kselftest, and HWCAP/HWCAP2 feature bits.

Risks: intentionally limits VQ coverage to architecture-relevant range plus one; future wider architectures may need updates. Big-endian SVE/FPSIMD comparisons are skipped. A typo in one fail message says `FPSMID`.

Test signals: fixed expected test count; failure messages identify unsupported access, flag handling, VL, FPSIMD conversion, or data mismatch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c -->
