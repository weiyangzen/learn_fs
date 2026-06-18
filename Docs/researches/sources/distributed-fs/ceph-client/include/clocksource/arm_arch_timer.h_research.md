# sources/distributed-fs/ceph-client/include/clocksource/arm_arch_timer.h

Purpose: public definitions for the ARM architected timer clocksource/clockevent subsystem.

Important APIs/types/functions: control and CNTHCTL bit masks, `enum arch_timer_reg`, `enum arch_timer_ppi_nr`, `enum arch_timer_spi_nr`, `struct arch_timer_kvm_info`, `struct arch_timer_mem_frame`, `struct arch_timer_mem`, `arch_timer_get_rate`, `arch_timer_read_counter`, `arch_timer_get_kvm_info`, and `arch_timer_evtstrm_available`.

Control flow: consumers query rate/counter/KVM info through exported functions when `CONFIG_ARM_ARCH_TIMER` is enabled; otherwise stubs return zero/false. Register enums and flags drive low-level timer setup in implementation files.

State and persistence: describes memory-mapped timer frame state and KVM-visible timecounter/IRQ state, but stores no state itself.

Dependencies and integration points: depends on `linux/timecounter.h`, bitops, and types. Integrates with ARM/arm64 clocksource drivers, KVM timer virtualization, event stream support, and device-tree/ACPI timer discovery.

Risks: incorrect IRQ enum use or user-access control flags can break timer interrupts, vDSO counter access, or guest timekeeping. Stubbed builds must not accidentally rely on nonzero timer data.

Test signals: ARM boot/timekeeping tests, KVM guest timer tests, clocksource selftests, and config coverage with `CONFIG_ARM_ARCH_TIMER` disabled.
