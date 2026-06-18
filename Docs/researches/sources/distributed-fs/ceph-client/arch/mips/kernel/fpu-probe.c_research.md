<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c

### Purpose
`fpu-probe.c` discovers MIPS FPU capabilities, records hardware or emulator feature bits in `struct cpuinfo_mips`, and applies boot-time policy for IEEE 754 legacy NaN versus 2008 NaN behavior. It supports both real CP1 hardware and the in-kernel FPU emulator, and it exposes the `nofpu` and `ieee754=` boot controls used during early CPU setup.

### Important APIs, Types, And Functions
The externally visible functions are `__cpu_has_fpu()`, `cpu_set_fpu_opts()`, `cpu_set_nofpu_opts()`, and the global `mips_fpu_disabled`. Internal helpers include `cpu_get_fpu_id()`, `cpu_set_fpu_fcsr_mask()`, `cpu_set_fpu_2008()`, `cpu_set_nofpu_2008()`, `cpu_set_nan_2008()`, and `cpu_set_nofpu_id()`. The local `ieee754` enum accepts `STRICT`, `EMULATED`, `LEGACY`, `STD2008`, and `RELAXED`, selected by `early_param("ieee754", ...)`.

### Control Flow
Hardware probing temporarily enables CP1 with `__enable_fpu(FPU_AS_IS)`, reads FIR/FCSR, probes writable FCSR mask bits by writing forced-zero and forced-one patterns, and restores CP0 status and FCSR. NaN/ABS2008 support is inferred from FIR and FCSR writability, then filtered by `ieee754=`. The `nofpu` setup path calls `cpu_set_nofpu_opts()` on `boot_cpu_data`, clears `MIPS_CPU_FPU`, builds an emulated FIR, and sets `mips_fpu_disabled`.

### State, Persistence, And Dependencies
State is stored in `boot_cpu_data` or the supplied `cpuinfo_mips`: `fpu_id`, `fpu_csr31`, `fpu_msk31`, `options`, and `ases`. Global policy state includes `mips_use_nan_legacy`, `mips_use_nan_2008`, `mips_nofpu_msk31`, and `mips_fpu_disabled`. The file depends on CP0/CP1 register accessors, `asm/fpu.h`, CPU feature flags, and ELF NaN compatibility globals.

### Integration Points
This code is consumed by MIPS CPU probing, ELF binary compatibility checks, lazy FPU ownership, FPU exception handling, and the software FPU emulator. `fpu-probe.h` provides no-op stubs when `CONFIG_MIPS_FP_SUPPORT` is absent.

### Risks
The riskiest behavior is writing and restoring FCSR/CP0 state during early CPU probing. Wrong FCSR masks can expose unsupported user-visible floating-point modes, and an incorrect NaN policy can reject valid binaries or allow binaries whose NaN encoding the hardware cannot execute. `nofpu` relies on the boot CPU mask saved from hardware probing, so boot ordering matters.

### Test Signals
High-signal tests include booting with `ieee754=strict`, `legacy`, `2008`, `emulated`, and `relaxed`, booting with `nofpu`, checking ELF NaN acceptance/rejection paths, running FPU exception tests, and validating `/proc/cpuinfo`/feature flags on CPUs with and without real CP1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c -->
