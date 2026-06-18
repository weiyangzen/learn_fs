# sources/distributed-fs/ceph-client/arch/x86/kernel/vsmp_64.c

Purpose: performs early initialization for ScaleMP vSMPowered x86-64 systems, including detection, optional CPU count capping, and control-register programming.

Important APIs/functions: public entry is `vsmp_init()`. Internal helpers are `detect_vsmp_box()`, `is_vsmp_box()`, `vsmp_cap_cpus()`, and `set_vsmp_ctl()`.

Control flow: `vsmp_init()` probes PCI bus 0 device 0x1f function 0 for ScaleMP vendor/device IDs when early PCI is allowed. If detected, it optionally caps `setup_max_cpus` to the first-board topology when `CONFIG_X86_VSMP` is unset, then maps the vSMP control BAR, logs capabilities/control values, clears the interrupt routing bit when the foundation can route interrupts optimally, disables user IRQ affinity changes via procfs where applicable, writes the updated control register, and unmaps.

State and persistence: `is_vsmp` caches detection state. `setup_max_cpus` and `no_irq_affinity` may be changed during early boot. The vSMP control register write persists in platform firmware/hardware behavior for the running kernel.

Dependencies and integration: depends on CONFIG_PCI, early PCI config access, early ioremap, SMP setup globals, procfs IRQ affinity flag, PCI IDs, and x86 setup ordering before full PCI/resource initialization.

Risks: incorrect detection or BAR mapping can touch wrong MMIO. CPU capping is a functional limitation when the kernel lacks full vSMP support. IRQ affinity disabling changes administrative behavior but is required for platform-routed interrupts.

Test signals: boot logs showing vSMP CTL capabilities/control and optional CPU cap, correct CPU count on unsupported/full-support builds, and stable interrupt routing on ScaleMP hardware.
