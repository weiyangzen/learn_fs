<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c

Purpose: Implements an exported allocator/control API for Freescale MPIC global timers, including long-duration cascaded timer pairs.

Important APIs/types/functions: Exports `mpic_request_timer()`, `mpic_start_timer()`, `mpic_stop_timer()`, `mpic_get_remain_time()`, and `mpic_free_timer()`. Important types are `timer_regs`, `cascade_priv`, `timer_group_priv`, and `struct mpic_timer` from `asm/mpic_timer.h`.

Control flow: Subsys init scans `fsl,mpic-global-timer` nodes and initializes each timer group by mapping timer registers and TCR, deriving frequency, parsing available timer IRQ ranges, setting idle bits, applying clock divider, and adding the group to a global list. Requests convert seconds to ticks, pick an idle single timer or cascade pair, program base/current counts stopped, request the timer IRQ, and return a handle. Start clears `TIMER_STOP`; stop sets it and clears current counts; free stops, frees IRQ, clears cascade mode if used, and marks timers idle.

State and persistence: Persistent state is `timer_group_list`, per-group MMIO/TCR mappings, timer frequency, idle bitmap, per-timer IRQ/number/dev/cascade handle, and cascade TCR bits. Hardware counter/base/count registers hold live timer state.

Dependencies and integration points: Depends on OF resources/IRQs, MPIC global timer hardware, `fsl,mpic` clock-frequency, syscore resume, exported timer clients, and IRQF_TRIGGER_LOW timer interrupts.

Risks: Time arguments are `time64_t` seconds converted directly to ticks; precision is coarse and overflow is rejected. Cascade allocation consumes adjacent timers and must correctly restore TCR bits on free. `mpic_request_timer()` calls `mpic_free_timer()` on `request_irq()` failure even though IRQ was not registered, so failure paths rely on `free_irq()` tolerance through that helper.

Test signals: Timer request/start/stop/free, remaining-time reads, cascade long-duration allocation, available-ranges parsing, frequency/divider correctness, IRQ firing, resume reinitialization, and concurrent timer allocation.

Source read size: 560 lines, 12761 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c -->
