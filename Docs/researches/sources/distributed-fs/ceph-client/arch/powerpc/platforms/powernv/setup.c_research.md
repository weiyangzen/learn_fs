## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/setup.c

### Purpose
`setup.c` defines the PowerNV machine descriptor and the platform lifecycle: firmware feature discovery, security mitigation setup, SMP/interrupt startup, reboot/poweroff, kexec teardown, transactional memory enablement, and CPU info reporting.

### Important APIs, Types, And Functions
Important functions include `pnv_setup_security_mitigations()`, `pnv_setup_arch()`, `pnv_init()`, `pnv_init_IRQ()`, `pnv_restart()`, `pnv_power_off()`, `pnv_shutdown()`, `pnv_kexec_cpu_down()`, `pnv_setup_machdep_opal()`, `pnv_probe()`, `pnv_tm_init()`, `pnv_get_proc_freq()`, and `define_machine(powernv)`.

### Control Flow
`pnv_probe()` detects OPAL firmware, installs OPAL machdep callbacks, and performs early platform init. `setup_arch` then configures speculation mitigations from `/ibm,opal/fw-features`, initializes SMP, NVRAM, NAP power save, guarded-core warnings, and RNG. IRQ init prefers native XIVE and falls back to XICS. Shutdown paths stop OPAL events, stop secondary CPUs, disable interrupts, and loop in OPAL reboot/poweroff calls until completion or fallback.

### State, Persistence, And Dependencies
State is mostly global architecture callback state: `ppc_md`, `pm_power_off`, security feature flags, `powersave_nap`, CPU feature bits, hardware description strings, PACA MCE buffers, and kexec state. Dependencies include OPAL, XIVE/XICS, PCI, memblock, CPU feature tables, transactional memory flags, and security mitigation helpers.

### Integration Points
The machine descriptor plugs this code into generic PowerPC boot, `/proc/cpuinfo`, PCI discovery, machine shutdown, memory hotplug block sizing, kexec CPU teardown, and early machine-check recovery.

### Risks
Mitigation policy depends on exact firmware feature names and default-on/default-off semantics. Reboot and poweroff loops can spin forever if OPAL never completes. Kexec teardown must put CPUs and interrupt controllers into a state the next kernel can use.

### Test Signals
PowerNV boot on hash/radix systems, `/proc/cpuinfo`, OPAL reboot modes (`full`, `fast`, `mpipl`, `error`), kexec/kdump, XIVE/XICS fallback, firmware-feature DT variants, and TM enabling on POWER9 are key signals.
