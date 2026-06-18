<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/n64/init.c

### Purpose
`n64/init.c` implements basic Nintendo 64 platform setup: command line initialization, memory resource bounds, memblock RAM declaration, fixed timer frequency, platform devices for audio/cart/controller, and a simple framebuffer.

### Important APIs, Types, And Functions
`prom_init()` initializes firmware command line. `plat_mem_setup()` sets IO memory resource bounds and adds 8 MiB RAM. `plat_time_init()` sets `mips_hpt_frequency`. `n64_platform_init()` registers `n64audio`, `n64cart`, `n64joy`, programs RDP video registers, allocates framebuffer memory, and registers `simple-framebuffer`.

### Control Flow
At arch initcall, device resources are constructed for MI/AI/PI/SI register banks and RCP IRQ, then platform devices are registered. A DMA-capable framebuffer buffer is allocated with extra bytes, physically aligned to 64 bytes, and its address is written into the RDP register sequence for 320x240 NTSC output.

### State, Persistence, And Dependencies
Persistent state includes memblock RAM, IO resource boundaries, registered platform devices, allocated framebuffer memory, RDP register values, and timer frequency. Dependencies include platform device core, simplefb, raw MMIO writes through CKSEG1, firmware command-line helper, and MIPS CPU IRQ numbering.

### Integration Points
N64-specific audio/cart/joy drivers bind to these platform devices. The simple framebuffer gives early display output without a full DRM driver.

### Risks
The framebuffer allocation is never freed, by design, but allocation failure disables simplefb. RAM is hard-coded to 8 MiB with a note that bootloader blocks 4 MiB config. Video timing is fixed to NTSC 320x240 and the RDP register programming assumes hardware state.

### Test Signals
Boot on N64 or accurate emulator, verify 8 MiB memory map, timer rate, platform device probing, RCP IRQ delivery, and simplefb output with correct physical alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/init.c -->
