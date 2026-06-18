<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c

Purpose: polled memory-mapped button driver for Cobalt systems.

Important APIs/types/functions: `struct buttons_dev` stores keymap, debounce counters, and mapped register. `handle_buttons()` reads the status register, inverts/shifts it, debounces each bit using a count threshold, and reports `MSC_SCAN` plus key state. Probe maps the memory resource and registers a polled input device.

Control flow and state: platform probe maps IORESOURCE_MEM, copies the static keymap, sets input capabilities, installs polling at 30 ms, and registers input. Polling reports press after three consecutive active reads and release after an inactive read following an accepted press.

State and persistence behavior: debounce counters persist in memory. Hardware button state is read-only from the mapped register.

Dependencies and integration points: depends on platform resources, MMIO `readl`, input polling, and platform alias `Cobalt buttons`.

Risks: uses `devm_ioremap()` rather than resource-managed exclusive mapping. Status mask constant is defined but not used. Polling assumes active-low bits in the top byte and fixed key count.

Test signals: test resource absence, register mapping failure, debounce press/release timing, all key bits, MSC_SCAN values, and polling interval behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c -->
