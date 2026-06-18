# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.c

Purpose: `sh_css_hrt.c` provides low-level host runtime checks around SP/ISP hardware state. In this subset it implements idleness detection and a simple wait loop for SP completion or software interrupt notification.

Important APIs/types/functions: `sh_css_hrt_system_is_idle()` reads SP and ISP idle bits and checks every FIFO monitor channel for valid queued data. `sh_css_hrt_sp_wait()` polls until the SP idle bit is set or a SW interrupt bit appears in the IRQ controller status register. The header declares additional SP start functions, but this file only implements idle and wait.

Control flow and state: `sh_css_hrt_system_is_idle()` accumulates `not_idle`, emits warnings for a non-idle SP, non-idle ISP, or non-empty FIFO channel, and returns the inverse. `sh_css_hrt_sp_wait()` busy-waits with `udelay(1)` while both "not idle" and "no SW interrupt" remain true, then returns 0. Neither function persists state.

Dependencies and integration: it uses inline accessors from `event_fifo.h`, `sp.h`, `isp.h`, `irq.h`, and `fifo_monitor.h`, plus `IA_CSS_WARNING` logging. It is used around CSS pipeline lifecycle and by parameter/shading code indirectly through runtime checks.

Risks: `sh_css_hrt_sp_wait()` has no timeout, so a wedged SP without an interrupt can spin indefinitely. Idleness relies on hardware register correctness and may race with concurrent SP/ISP activity. FIFO warnings are diagnostic only and do not identify owners of pending data.

Test signals: hardware or emulator tests should cover idle and busy SP/ISP states, pending FIFO data, SW interrupt wakeup, and stuck-SP timeout behavior at higher layers. Static review should confirm callers do not invoke the unbounded wait from contexts that cannot tolerate polling.
