<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c

### Purpose
`setup.c` initializes Jazz memory/I/O mappings, reserves legacy I/O resources, sets console and restart hooks, and registers platform devices for serial, SCSI, Ethernet, RTC, and speaker hardware.

### Important APIs, Types, And Functions
Important objects are `jazz_io_resources`, `plat_mem_setup()`, `jazz_serial_data`, `jazz_serial8250_device`, `jazz_esp_pdev`, `jazz_sonic_pdev`, `jazz_cmos_pdev`, `pcspeaker_pdev`, and `jazz_setup_devinit()`.

### Control Flow
Early platform setup installs wired TLB entries, sets the I/O port base, marks EISA presence when configured, reserves PC-compatible I/O ranges, assigns restart behavior, and selects `ttyS0` at 9600. Device initcall later registers serial8250, ESP SCSI, Sonic Ethernet, RTC CMOS, and PC speaker devices with fixed resources.

### State, Persistence, And Dependencies
Runtime state is wired TLB mappings, I/O resource reservations, platform device records, DMA masks, console preference, and restart hook. Dependencies include Jazz hardware constants, platform bus, serial8250, DMA mask helpers, and EISA state.

### Integration Points
Registered devices bind to generic drivers and to Jazz DMA operations. The fixed resources connect the platform to interrupt and DMA setup in `irq.c` and `jazzdma.c`.

### Risks
Hard-coded physical addresses, IRQs, and UART clock variants make board identification important. Repeated wired mappings overlap with `arch_init_irq()`, so mapping assumptions must remain aligned.

### Test Signals
Boot tests should confirm console output, serial ports, ESP SCSI probing, Sonic Ethernet DMA, RTC IRQ, PC speaker registration, I/O resource conflicts, and restart hook installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c -->
