# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_gtm.h

Purpose: Declares the Freescale General-purpose Timer Module 16-bit timer interface used by platform timer clients that need ownership, programming, stopping, and acknowledgement of GTM channels.

Important APIs, types, and functions: `struct gtm_timer` carries the IRQ number, parent `struct gtm`, allocation state, and `__iomem` register pointers for control, mode, prescale, counter, reference, and event registers. Exported APIs are `gtm_get_timer16()`, `gtm_get_specific_timer16()`, `gtm_put_timer16()`, `gtm_set_timer16()`, `gtm_set_exact_timer16()`, `gtm_stop_timer16()`, and `gtm_ack_timer16()`.

Control flow: Callers acquire an available timer, configure a relative or exact 16-bit timeout with optional reload, service the IRQ by acknowledging event bits, stop the timer when no longer needed, and release ownership with `gtm_put_timer16()`.

State and persistence: State is volatile hardware/MMIO state plus the in-memory `requested` ownership bit. There is no persistent storage; all programming is lost across reset or driver teardown.

Dependencies and integration points: Depends on Linux integer types and Freescale GTM implementation code that owns the opaque `struct gtm`. It integrates with interrupt handlers, board code, and SoC timer users that know a GTM instance or can use any available timer.

Risks: Ownership must be balanced or timers can leak. Register pointers are raw MMIO, so endian access, event acknowledgement masks, and reload calculations are hardware-sensitive. The microsecond API can overflow or quantize against a 16-bit counter.

Test signals: Exercise generic and specific timer allocation, release-after-stop, one-shot and reload programming, exact 16-bit boundary values, event acknowledgement, IRQ firing, and concurrent allocation failure paths.
