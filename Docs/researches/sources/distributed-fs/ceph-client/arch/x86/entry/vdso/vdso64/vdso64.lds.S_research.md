## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdso64.lds.S

Purpose: 64-bit vDSO linker/version script.

Important declarations: defines `BUILD_VDSO64`, includes the common layout, and exports `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, `__vdso_gettimeofday`, `getcpu`, `__vdso_getcpu`, `time`, `__vdso_time`, `clock_getres`, `__vdso_clock_getres`, optional `__vdso_sgx_enter_enclave`, `getrandom`, and `__vdso_getrandom` under `LINUX_2.6`.

Control flow: link-time symbol versioning only.

State/persistence: defines the user-visible dynamic symbol surface for the 64-bit vDSO image.

Integration points: vDSO objects, libc symbol resolution, SGX and getrandom vDSO implementations, and process mapping.

Risks: symbol-version changes break userspace ABI. Test signals include readelf version checks, vDSO selftests, SGX and getrandom availability checks under relevant configs.
