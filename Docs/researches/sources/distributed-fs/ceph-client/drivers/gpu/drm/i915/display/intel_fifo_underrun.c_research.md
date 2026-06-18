# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.c

Purpose: manages CPU pipe and PCH transcoder FIFO underrun reporting, logging, debug-register collection, immediate polling, and interrupt masking to avoid repeated underrun storms.

Important APIs/types/functions: public functions are `intel_init_fifo_underrun_reporting()`, `intel_set_cpu_fifo_underrun_reporting()`, `intel_set_pch_fifo_underrun_reporting()`, `intel_cpu_fifo_underrun_irq_handler()`, `intel_pch_fifo_underrun_irq_handler()`, `intel_check_cpu_fifo_underruns()`, and `intel_check_pch_fifo_underruns()`. Internal helpers handle underrun debug registers, GMCH PIPESTAT, ILK display IRQ bits, IVB `GEN7_ERR_INT`, BDW pipe IRQs, IBX/CPT south display interrupts, and shared interrupt enable policy.

Control flow: enabling reporting clears stale debug info where needed and unmasks the platform interrupt. IRQ handlers disable further reporting for the affected pipe/transcoder, log once, read and clear debug info, and notify FBC that underruns occurred. Polling paths check latch bits on platforms where interrupts are shared or absent. PCH reporting stores state in pipe-mapped CRTC fields, with special handling for LPT's single PCH transcoder.

State and persistence: per-CRTC `cpu_fifo_underrun_disabled` and `pch_fifo_underrun_disabled` persist across modesets until reinitialized or toggled. Debug status bits are hardware-latched and cleared by write. Interrupt mask state persists in display/PCH interrupt registers.

Dependencies and integration: integrates with `display->irq.lock`, intel display IRQ helpers, PCH display interrupt helpers, FBC underrun handling, tracepoints, pipe/transcoder helpers, and underrun debug register definitions in broader display regs.

Risks: several platforms have shared underrun interrupt enables, so disabling one pipe can suppress others. Debug bits can be stale unless cleared before reenable. IRQ handlers may run early during init. Missing FBC notification can leave FBC active after dangerous underruns.

Test signals: inject underruns on GMCH, ILK/SNB, IVB, BDW+, IBX, and CPT paths; verify one-shot logging, interrupt masking/unmasking around modesets, debug info clearing/logging, FBC disable response, and no interrupt storms.
