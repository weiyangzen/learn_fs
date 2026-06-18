# sources/distributed-fs/ceph-client/arch/mips/rb532/time.c

Purpose: RB532 timer frequency calibration. It sets the MIPS high-precision timer frequency from the firmware-provided CPU clock.

Important APIs and control flow: `cal_r4koff()` computes `mips_hpt_frequency = idt_cpu_freq * IDT_CLOCK_MULT / 2` and returns the per-HZ offset. `plat_time_init()` disables local interrupts, computes the offset, logs it and an estimated CPU frequency, then restores interrupts.

State, persistence, and integration: state is the global `mips_hpt_frequency` consumed by generic MIPS time code. It depends on `idt_cpu_freq` parsed by `prom.c` and the RC32434 counter running at half multiplied core speed. Risks include incorrect system time if firmware frequency is missing or malformed and no RTC fallback. Test signals are boot frequency log, stable jiffies, scheduler timing, and clock drift checks.
