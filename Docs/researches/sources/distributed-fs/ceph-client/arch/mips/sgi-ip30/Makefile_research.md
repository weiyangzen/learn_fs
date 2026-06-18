# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/Makefile

Purpose: build rules for SGI IP30 Octane support. It links HEART interrupt, power, setup, timer, and Xtalk code, with optional early console and SMP.

Important APIs and control flow: `obj-y` includes `ip30-irq.o ip30-power.o ip30-setup.o ip30-timer.o ip30-xtalk.o`. `ip30-console.o` is conditional on `CONFIG_EARLY_PRINTK`; `ip30-smp.o` is conditional on `CONFIG_SMP`.

State, persistence, and integration: no runtime state, but object selection controls machine hooks, timer/IRQ setup, and SMP operations. Dependencies include SGI IP30 config and optional SMP/early-printk choices. Risks include missing early debugging if early printk is off and no SMP operations if config mismatches hardware. Test signals are successful link and expected symbols.
