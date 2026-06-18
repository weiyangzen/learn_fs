<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c

Purpose: Gumstix AM300 EPD carrier support for a Broadsheet display controller on PXA25x GPIOs, including a bit-banged 16-bit host data bus.

Important APIs and functions: exposes `am300_init()` as a carrier hook. It registers `broadsheetfb` platform data through `struct broadsheet_board`. Callbacks include `am300_init_board()`, `am300_cleanup()`, `am300_set_hdb()`, `am300_get_hdb()`, `am300_set_ctl()`, `am300_wait_event()`, `am300_get_panel_type()`, and `am300_setup_irq()`.

Control flow: `am300_init()` configures MFP pins, requests `broadsheetfb`, allocates a platform device, attaches a copy of the board callback table, and adds the device. Driver probe then calls board init, which requests control GPIOs plus GPIO58-73 for the data bus, sets initial output/input directions, resets the controller, and waits for RDY. IRQ setup binds RDY GPIO to a rising-edge interrupt.

State and persistence: static `am300_device` and `am300_board` persist after init; GPIO ownership, IRQ binding, and panel type parameter are runtime state. Data bus values are transient GPIO levels.

Dependencies and integration: depends on Gumstix carrier dispatch, PXA2xx MFP macros, GPIO, PXA IRQ mapping, and `broadsheetfb`.

Risks and test signals: `am300_wait_event()` waits without timeout, so missing RDY can hang probe/control operations. The DB request error label reuses loop state and should be tested for partial failures. Test with GPIO request failure injection, RDY IRQ, panel type parameter, and read/write correctness on the 16-bit HDB bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c -->
