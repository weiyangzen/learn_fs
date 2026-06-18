## sources/distributed-fs/ceph-client/drivers/w1/masters/omap_hdq.c

Purpose: this platform driver supports TI OMAP HDQ/1-Wire hardware and exposes it through the w1 core, either in HDQ-style single-device mode or 1-Wire mode.

Important APIs/types/functions: `struct hdq_data` stores device, MMIO base, transaction mutex, IRQ status with spinlock, and mode. Low-level helpers handle register I/O, flag waits, IRQ status reset, byte write/read, break pulse, and ISR. W1 callbacks include `omap_w1_search_bus()`, `omap_w1_triplet()`, `omap_w1_reset_bus()`, `omap_w1_read_byte()`, and `omap_w1_write_byte()`.

Control flow: probe maps registers, reads `ti,mode`, configures either synthetic HDQ search or true 1-Wire triplet, enables runtime PM/autosuspend, reads hardware revision, requests IRQ, issues a break pulse, registers a global `omap_w1_master`, and releases runtime PM. Transactions take runtime PM references, serialize on `hdq_mutex`, program control/status bits, wait for IRQ status through a wait queue, clear consumed IRQ bits under spinlock, and drop PM references. Runtime suspend stores mode and clears interrupt status; resume enables clock and interrupt mask.

State and persistence behavior: `hdq_irqstatus` accumulates interrupt bits until consumed. `mode` persists selected HDQ/1W mode. The module parameter `w1_id` controls the synthetic ROM ID in HDQ mode. The w1 master object is static and populated at probe time.

Dependencies and integration points: depends on platform resources, device tree compatibles `ti,omap3-1w` and `ti,am4372-hdq`, runtime PM, IRQs, w1 core, and w1 CRC helper.

Risks: global static `omap_w1_master` limits multi-instance safety. Some callbacks return negative errors through `u8`, collapsing to `0xff`. Break/reset ignores `omap_hdq_break()` failure and returns success. Timing and IRQ completion are hardware-sensitive.

Test signals: HDQ and 1-Wire modes, runtime suspend/resume around transactions, IRQ timeout and status clearing, triplet ROM search, SKIP ROM break behavior, module `w1_id`, remove while runtime suspended, and multiple-controller probe attempts.
