# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c

### Purpose
GPIO-controlled halt support for SGY CTS1000-style QorIQ GPIO hardware. It watches a child GPIO node and triggers orderly poweroff or halt behavior from GPIO interrupt/workqueue context.

### Important APIs, Types, And Functions
Important objects are global `halt_gpio`, `child_match`, `gpio_halt_wfn()`, `gpio_halt_irq()`, `__gpio_halt_probe()`, `gpio_halt_probe()`, `gpio_halt_remove()`, `gpio_halt_match`, and `gpio_halt_driver`. It matches `fsl,qoriq-gpio` parents and `sgy,gpio-halt` child nodes.

### Control Flow
Probe finds the halt child node, requests the GPIO descriptor, converts it to an IRQ, installs an interrupt handler, and schedules work when triggered. The work function samples the GPIO and performs the halt path. Remove cancels work and releases resources through managed APIs where applicable.

### State, Persistence, And Dependencies
State includes the global GPIO descriptor, IRQ registration, and scheduled work. No durable persistence exists. Dependencies include GPIO descriptors, OF child matching, platform driver registration, IRQ APIs, and power-management/halt helpers.

### Integration Points
Hooks board-level shutdown hardware into Linux platform-driver and GPIO subsystems.

### Risks
Global `halt_gpio` means only one active instance is expected. IRQ polarity/debounce/device-tree errors can cause false shutdowns or missed halt requests.

### Test Signals
Probe with a CTS1000 DT, toggle the halt GPIO, verify IRQ/workqueue behavior, shutdown action, and clean driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c -->
