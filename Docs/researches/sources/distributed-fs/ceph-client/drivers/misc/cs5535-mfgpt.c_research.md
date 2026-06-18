# sources/distributed-fs/ceph-client/drivers/misc/cs5535-mfgpt.c

Purpose: implements a platform driver and exported allocator/control API for AMD Geode CS5535/CS5536 multi-function general purpose timers (MFGPTs).

Important APIs, types, and functions: exported functions are `cs5535_mfgpt_toggle_event()`, `cs5535_mfgpt_set_irq()`, `cs5535_mfgpt_alloc_timer()`, `cs5535_mfgpt_free_timer()`, `cs5535_mfgpt_read()`, and `cs5535_mfgpt_write()`. `struct cs5535_mfgpt_timer` describes an allocated timer and `cs5535_mfgpt_chip` stores global device state. Module parameter `mfgptfix` optionally resets timers during init.

Control flow: platform probe validates `mfgptfix`, reserves the I/O region, initializes global chip state, scans available timers, and marks the chip initialized. `scan_timers()` optionally performs undocumented full reset or soft reset, then reads each timer setup register and marks free timers in a bitmap. Allocation selects a requested or first available timer from the bitmap under a spinlock, allocates a handle, and clears the availability bit. Freeing only returns a timer to the bitmap if its setup bit was never programmed. Event toggling manipulates MSRs for reset, NMI, or IRQ routing. IRQ setup checks shared-twin/VSA constraints, existing/default IRQ selection, LPC routing, and then enables the IRQ event.

State and persistence: the driver has one static global chip with availability bitmap, base I/O address, platform device pointer, lock, and initialized flag. Hardware timer setup, comparator events, IRQ routing, and MSR state persist in chipset registers beyond the lifetime of an allocated handle unless explicitly reset.

Dependencies and integration points: depends on platform devices named `cs5535-mfgpt`, Geode `linux/cs5535.h`, x86 MSR access, inw/outw port I/O, and client drivers that allocate timers for watchdog/clock/event functions.

Risks: the reset modes are intentionally broad and can disturb firmware-owned timers. `soft_reset()` constructs a temporary timer without initializing `.chip`, so calls through `cs5535_mfgpt_toggle_event()` only work because that function uses `timer->nr` and MSRs, not `chip`. IRQ routing can conflict with VSA or other Linux users if forced. Freeing does not reset programmed hardware, so resource reuse is conservative and may surprise callers.

Test signals: probe with valid and invalid `mfgptfix` values, timer allocation/free for requested and automatic timers, IRQ routing success/failure cases, read/write register access, and client-driver behavior on systems with firmware-reserved timers. Hardware/virtual Geode coverage is required for meaningful tests.
