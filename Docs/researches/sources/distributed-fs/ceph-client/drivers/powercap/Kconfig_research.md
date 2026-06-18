# sources/distributed-fs/ceph-client/drivers/powercap/Kconfig

## Purpose
`drivers/powercap/Kconfig` defines configuration options for the generic powercap sysfs framework and its client drivers: Intel RAPL, idle injection, ARM SCMI Powercap, and DTPM backends.

## Important APIs, Types, And Functions
This is Kconfig data rather than C code. `menuconfig POWERCAP` gates the subtree. `INTEL_RAPL_CORE` is a hidden tristate selected by MSR/TPMI RAPL drivers. `IDLE_INJECT`, `ARM_SCMI_POWERCAP`, `DTPM`, `DTPM_CPU`, and `DTPM_DEVFREQ` define build-time inclusion and dependencies.

## Control Flow
If `POWERCAP` is disabled, all nested options are unavailable. Enabling Intel MSR or TPMI RAPL selects `INTEL_RAPL_CORE`. `DTPM_CPU` and `DTPM_DEVFREQ` depend on `DTPM` and `ENERGY_MODEL`; CPU additionally requires SMP. `IDLE_INJECT` depends on CPU idle support. `ARM_SCMI_POWERCAP` depends on SCMI protocol support.

## State, Persistence, And Dependencies
The file persists no runtime state; it controls compile-time objects. Dependencies directly align with subsystem integration points: PCI/IOSF for Intel RAPL core, x86 and TPMI for Intel interfaces, CPU_IDLE for idle injection, ARM_SCMI_PROTOCOL for SCMI, OF/ENERGY_MODEL/SMP for DTPM.

## Integration Points
The selected symbols are consumed by the Makefile in the same directory and by conditional compilation in `dtpm_subsys.h`.

## Risks
`DTPM` is marked experimental in the prompt text but has no explicit `depends on EXPERT` or warning gate. `INTEL_RAPL_CORE` depends on PCI and selects IOSF_MBI, so build coverage should include both MSR and TPMI paths. `IDLE_INJECT` is bool only, reflecting early init/per-CPU thread design.

## Test Signals
Build-test representative configs: `POWERCAP=n`, Intel MSR, Intel TPMI, `IDLE_INJECT=y` without CPU_IDLE rejection, `ARM_SCMI_POWERCAP=m`, `DTPM=y` with and without CPU/devfreq backends, and dependency failure cases.
