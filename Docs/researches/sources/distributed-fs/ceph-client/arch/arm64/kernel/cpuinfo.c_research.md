## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c` captures ARM64 CPU identity and
feature-register snapshots, exposes `/proc/cpuinfo`, and publishes selected per-CPU ID registers
through sysfs. It provides the raw CPU data consumed by `cpufeature.c` to build sanitized system
feature state.

### Important APIs, Types, And Functions
The core storage is `DEFINE_PER_CPU(struct cpuinfo_arm64, cpu_data)`, plus `boot_cpu_data` and
`__icache_flags`. User-visible feature names live in `hwcap_str[]` and, under `CONFIG_COMPAT`,
`compat_hwcap_str[]` and `compat_hwcap2_str[]`. `/proc/cpuinfo` is served by `cpuinfo_op` using
`c_start()`, `c_next()`, `c_stop()`, and `c_show()`. Sysfs register exposure uses
`CPUREGS_ATTR_RO()`, `cpuid_cpu_online()`, `cpuid_cpu_offline()`, and `cpuinfo_regs_init()`.
Hardware capture is performed by `__cpuinfo_store_cpu()`, `__cpuinfo_store_cpu_32bit()`,
`cpuinfo_store_cpu()`, and `cpuinfo_store_boot_cpu()`.

### Control Flow
On the boot CPU, `cpuinfo_store_boot_cpu()` reads architectural registers into per-CPU CPU0 data,
copies them to `boot_cpu_data`, and calls `init_cpu_features()`. On secondary CPU startup,
`cpuinfo_store_cpu()` refreshes this CPU's snapshot and calls `update_cpu_features()` to fold the
CPU into the sanitized system state or verify it after finalization. `__cpuinfo_store_cpu()` reads
the effective cache type, DC ZVA size, MIDR/REVIDR/AIDR, AArch64 ID registers, optional GMID, SMIDR,
and AArch32 registers only if 32-bit EL0 is supported. MPAMIDR is deliberately deferred to
`cpufeature.c` so overrides can prevent unsafe firmware traps.

For reporting, `/proc/cpuinfo` iterates online CPUs and prints processor number, BogoMIPS, HWCAP
feature strings, implementer, architecture, variant, part, and revision. Sysfs hotplug callbacks add
a `regs/identification` group under each CPU device containing MIDR, REVIDR, AIDR, and optionally
SMIDR when SME is supported.

### State, Persistence, And Dependencies
The file persists data only in kernel memory and sysfs/procfs views. `__icache_flags` records
whether any CPU has an aliasing I-cache. Dependencies include CPU ID/system-register accessors,
`arch_timer_get_cntfrq()`, cpumasks, CPU hotplug, kobjects/sysfs, `loops_per_jiffy`, personality
handling for compat `/proc/cpuinfo`, `cpufeature.c` exports, and SME/MTE/MPAM feature helpers.

### Integration Points
`cpufeature.c` consumes these snapshots for all feature sanitization and CPU capability decisions.
`/proc/cpuinfo` is consumed by legacy userspace and libc CPU enumeration behavior, while sysfs
register files are consumed by diagnostic tools. Cache policy detection feeds global I-cache
maintenance decisions that affect executable mappings and JIT coherency.

### Risks
Reading unavailable or firmware-trapped registers too early can crash or hang boot, which is why
some optional registers are gated. Misreporting HWCAP names can break user-space feature dispatch.
Incorrect cache-type interpretation can produce stale instruction execution or excessive cache
maintenance. Hotplug sysfs lifetime errors can leak or double-remove kobjects. Compat reporting is
ABI-sensitive because older software parses strings rather than auxv.

### Test Signals
Boot and hotplug on varied ARM64 CPUs, `/proc/cpuinfo` comparison against auxv, sysfs
`/sys/devices/system/cpu/cpu*/regs/identification/*` reads across online/offline transitions,
compat process checks, SME-enabled builds, and cache aliasing/JIT tests are the main validation
signals.
