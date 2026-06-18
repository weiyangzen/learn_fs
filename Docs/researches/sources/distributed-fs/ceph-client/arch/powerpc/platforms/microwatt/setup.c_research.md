# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/setup.c

Purpose: Microwatt machine descriptor for interrupts, OF platform population, RNG setup, SMP release, and idle wait.

Important APIs and control flow: `microwatt_probe` always matches compatible `microwatt-soc` and calls `microwatt_init_smp` when SMP is enabled. `microwatt_init_IRQ` initializes XICS. A machine arch initcall runs `of_platform_default_populate`. `microwatt_setup_arch` initializes DARN RNG. `microwatt_idle` prepares for irqsoff idle and executes `wait`. `define_machine(microwatt)` wires progress, power-save, setup, and IRQ callbacks.

State, dependencies, and risks: state is `ppc_md` callbacks and any SMP/RNG state initialized by sibling files. Dependencies include XICS native support, OF compatible string, default platform bus population, udbg, and the CPU `wait` instruction. Risks include unconditional probe return for compatible systems, idle correctness around interrupt preparation, and SMP setup before full device-tree unflattening. Test signals are Microwatt boot, XICS interrupt handling, device population, idle wakeups, RNG callback, and SMP bring-up when configured.
