# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/smp-shx3.c

Purpose: implements SH-X3 platform SMP operations: CPU discovery mapping, IPI request/handling, secondary CPU startup, CPU hotplug preparation, and CPU id lookup.

Important APIs, types, and functions: `shx3_smp_ops` exports `struct plat_smp_ops`. Key functions are `ipi_interrupt_handler()`, `shx3_smp_setup()`, `shx3_prepare_cpus()`, `shx3_start_cpu()`, `shx3_smp_processor_id()`, `shx3_send_ipi()`, `shx3_update_boot_vector()`, and `shx3_cpu_prepare()`. `register_shx3_cpu_notifier()` installs a CPU hotplug prepare state.

Control flow: SMP setup marks CPU0 possible and then naively marks CPUs up to `NR_CPUS` as possible. `prepare_cpus()` requests per-CPU IPI IRQs starting at 104 and marks CPUs present. Starting a CPU writes the reset vector to a per-CPU RESET register, stops the target via STBCR MSTP, then releases it with reset/light-sleep bits. IPIs write a message bit to per-CPU INTICI registers; the handler clears and dispatches the message to `smp_message_recv()`.

State and persistence: CPU maps `__cpu_number_map` and `__cpu_logical_map` are initialized. Hardware state lives in per-CPU STBCR/RESET registers and interrupt controller IPI registers. Hotplug prepare rewrites boot vectors before CPU bring-up.

Dependencies and integration points: integrates with Linux SMP, CPU hotplug (`cpuhp_setup_state_nocalls`), native SuperH CPU idle/death helpers, SH-X3 INTC vectors from setup files, and 29-bit vs physical address handling.

Risks: CPU count probing is intentionally absent; every `NR_CPUS` slot is marked possible, which can expose nonexistent CPUs. `BUG_ON(cpu >= 4)` in IPI send assumes hardware max 4. Startup loops can spin forever if STBCR bits do not update.

Test signals: boot should report expected secondary CPUs, CPU bring-up/hotplug should succeed, IPIs should deliver scheduler and TLB messages, `/proc/interrupts` should show IPI IRQs, and CPU id register reads should match logical maps.
