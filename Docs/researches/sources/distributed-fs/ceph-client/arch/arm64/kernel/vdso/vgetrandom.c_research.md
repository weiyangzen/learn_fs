## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom.c

### Purpose
`vgetrandom.c` is the native VDSO wrapper for `__kernel_getrandom`, selecting the fast generic VDSO implementation when FPSIMD is available and falling back to the real syscall otherwise.

### Important APIs, Types, And Functions
It defines `__kernel_getrandom` with the same type as `__cvdso_getrandom` and uses `alternative_has_cap_likely(ARM64_HAS_FPSIMD)`, `getrandom_syscall`, and a special probe case returning `-ENOSYS`.

### Control Flow
On CPUs with finalized FPSIMD support, the wrapper calls `__cvdso_getrandom`. Without FPSIMD it returns `-ENOSYS` for the opaque-state probe convention or invokes the kernel syscall fallback for normal requests.

### State, Persistence, And Dependencies
It owns no persistent state. The generic VDSO random code and kernel RNG state provide data and opaque state semantics.

### Integration Points
Built into the native VDSO, exported by the linker script, and tied to `vgetrandom-chacha.S` and generic `vdso/getrandom` support.

### Risks
Incorrect capability gating can execute SIMD code when unavailable or miss the fast path. The probe ABI must return `-ENOSYS` exactly for unsupported VDSO operation.

### Test Signals
Run getrandom VDSO tests on FPSIMD-capable and capability-disabled configurations, verify syscall fallback and probe behavior, and compare output/error handling with the syscall ABI.
