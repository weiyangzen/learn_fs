# Group Research: Plan 9 PC Device and Network Drivers

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlm78.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlm78.c

Read completely: 346 lines.

This file implements the Plan 9 `#T` LM78 hardware monitor device. It exposes one file, `lm78vram`, backed by the LM78 value RAM registers `0x20..0x3f`.

Key behavior:
- Detects LM78 access through Intel PIIX/PIIX3 parallel port mapping or PIIX4 SMBus.
- `lm78reset()` probes PCI bridges and configures either `Parallel` or `Smbus` mode.
- `lm78enable()` verifies the chip address register and starts sampling without changing BIOS-configured interrupt/alarm masks.
- `lm78read()` reads byte ranges from value RAM.
- `lm78write()` can write value RAM offsets, despite the directory entry being mode `0444`.

Important interfaces:
- Device name: `lm78`, rune `'T'`.
- Files: `#T/lm78vram`.
- Uses `SMBus`, `piix4smbus()`, `pcimatch()`, `pcicfgr16()`, `pcicfgw16()`, `inb/outb`.

Research notes:
- Locking is centralized with `lm78` as a `QLock` around register access.
- SMBus reads are implemented as `SMBsend` followed by `SMBrecv`.
- The driver intentionally does not implement LM78 management interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlm78.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlml.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlml.c

Read completely: 403 lines.

This file implements a Plan 9 video device for LML/Zoran Motion JPEG capture hardware. It registers as the `video` device using rune `Λ`.

Key behavior:
- Probes PCI Zoran `36067` devices in `lmlreset()`.
- Allocates page-aligned `CodeData` buffers shared with hardware.
- Registers physical segments named `lmlN.mjpg` and `lmlN.regs`.
- Publishes per-card files: `lmlNctl`, `lmlNjpg`, and `lmlNraw`.
- Captured frame metadata is returned through reads of size `sizeof(FrameHeader)` or one byte for buffer number.
- Interrupt handler `lmlintr()` detects JPEG completion, updates embedded frame headers, and wakes readers.

Important interfaces:
- Depends on `devlml.h` for hardware structures and constants.
- Uses PCI mapping through `vmap()`, interrupt registration through `intrenable()`, and physical segment registration through `addphysseg()`.
- `lmlread()` on control files reports mapped register and MJPEG buffer physical locations.

Research notes:
- Only read opens are allowed, even for `lmlNctl`.
- `jpgopens` enforces one active capture stream per card.
- The raw and jpg file paths both use `jpgread()`, with raw using non-sleeping behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlml.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlml.h

Read completely: 124 lines.

This header defines constants and DMA-visible data structures for the LML/Zoran Motion JPEG driver.

Key contents:
- Driver identity and sizing constants: `MJPG_VERSION`, `NLML`, `NBUF`, `FRAGSIZE`.
- Timeout and delay tunables for I2C, guest bus, and still capture polling.
- Zoran PCI identifiers and I2C addresses for BT819/BT856 companion chips.
- JPEG-like frame metadata structures:
  - `FrameHeader`
  - `Fragment`
  - `HdrFragment`
  - `FragmentTable`
  - `CodeData`

Important layout:
- Several structures are marked by comments as hardware-visible and should not be modified casually.
- `CodeData` contains physical pointers for the MJPEG status command area, grab buffer, fragment descriptors, and fragment buffers.
- `Codedatasize` and `Grabdatasize` are rounded to page size.

Research notes:
- The header assumes little-endian marker layout for SOI/APP3 markers.
- It is tightly coupled to `devlml.c`; no independent functions are defined here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlpt.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlpt.c

Read completely: 241 lines.

This file implements the Plan 9 Centronics parallel printer port device `#L`.

Key behavior:
- Supports three base addresses: `0x378`, `0x3bc`, and `0x278`.
- Attaching `#L` optionally selects a printer number.
- Exposes per-port files generated as `lptNdlr`, `lptNpsr`, `lptNpcr`, and `lptNdata`.
- `dlr`, `psr`, and `pcr` map to hardware registers.
- Writes to `data` send bytes using strobe control and wait for printer readiness.
- Interrupt handler wakes sleepers waiting for `Fnotbusy`.

Important interfaces:
- Device name: `lpt`, rune `'L'`.
- Uses `ioalloc()`, `intrenable(IrqLPT, ...)`, `inb/outb`, and `Rendez`.

Research notes:
- ECP ports are detected through the extended control register and forced toward PS/2-compatible mode when possible.
- `lptgen()` encodes hardware register addresses directly into Qid paths for non-data entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devlpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devpccard.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devpccard.c

Read completely: 1920 lines.

This file implements Plan 9 CardBus and 16-bit PCMCIA support, exposed as device `#Y` named `cardbus`.

Key behavior:
- Detects supported CardBus bridges from TI, Ricoh, and O2Micro.
- Maintains up to four slots in `cbslots`.
- Uses a state machine for `SlotEmpty`, `SlotFull`, `SlotPowered`, and `SlotConfigured`.
- Handles events: card detected, powered, ejected, and configured.
- CardBus PCI cards are scanned as subordinate PCI buses and assigned memory/I/O windows.
- 16-bit PCMCIA cards use legacy i82365-compatible registers, CIS parsing, memory windows, I/O windows, IRQ routing, and config-register writes.
- Exposes per-slot control files `cbNctl`.

Important interfaces:
- Device name: `cardbus`, rune `'Y'`.
- Files: `#Y/cbNctl`.
- Installs global hooks `_pcmspecial` and `_pcmspecialclose` so legacy drivers can claim PCMCIA cards by version string.
- Uses PCI bridge config registers, socket event/status registers, and legacy index/data ports at `0x3e0/0x3e1`.

Key internal pieces:
- `devpccardlink()` discovers bridges, maps controller registers, initializes interrupts, and starts card detection.
- `configure()` handles 32-bit CardBus PCI resource allocation.
- `i82365configure()` maps attribute memory and parses CIS tuples.
- `pccard_pcmspecial()` selects a matching 16-bit card, configures I/O ranges, IRQ, voltage, and optional config-register index.
- CIS tuple handlers include `tvers1`, `tcfig`, and `tentry`.

Research notes:
- The file combines kernel device namespace code, PCI bridge management, PCMCIA CIS decoding, and legacy card allocation.
- `pccardwrite()` supports `down <device>` and `power`.
- Some paths are explicitly incomplete, including PC16 unconfigure and memory-region file entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devpccard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devrtc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devrtc.c

Read completely: 461 lines.

This file implements the PC real-time clock and non-volatile RAM device `#r`.

Key behavior:
- Uses I/O ports `0x70` and `0x71`.
- Exposes `rtc` and `nvram`.
- `rtctime()` repeatedly reads CMOS BCD clock fields until two consecutive reads match.
- `rtcwrite()` accepts seconds since Unix epoch and writes BCD fields back to CMOS.
- `nvramread()` and `nvramwrite()` provide direct helpers for other kernel code.
- Device access restricts writes to `eve`.

Important interfaces:
- Device name: `rtc`, rune `'r'`.
- Files: `#r/rtc`, `#r/nvram`.
- Uses `readnum()` for textual RTC reads and direct byte copying for NVRAM.

Research notes:
- NVRAM user-visible space starts at CMOS offset `128` and has size `256`.
- Year conversion maps `00..69` to 2000-based years and `70..99` to 1900-based years.
- Calendar conversion functions implement leap-year handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devtv.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devtv.c

Read completely: 2194 lines.

This file implements a Plan 9 Brooktree Bt848/Bt878 TV capture driver exposed as `#V`.

Key behavior:
- Probes Bt848/Bt878 PCI devices.
- Detects board variants and tuners through I2C EEPROMs and GPIO state.
- Supports Miro, Miro Pro, and Hauppauge Bt878-style boards.
- Exposes per-card directories `tvN` with `video`, `audio`, `ctl`, and `regs`.
- Initializes Bt848 video capture registers for NTSC-sized `640x480` active frames.
- Builds Brooktree RISC DMA programs for packed RGB16 and planar YCbCr formats.
- Supports video capture into allocated frame buffers or direct VGA memory.
- Supports Bt878 audio capture with a separate RISC program and ring of audio blocks.
- Handles MSP3400 audio control, volume, mute, tuning, and audio-format status.
- Loads Hauppauge KFIR/Altera microcode from `hcwAMC.h`.

Important interfaces:
- Device name: `tv`, rune `'V'`.
- Control commands:
  - `vstart`
  - `vgastart`
  - `vstop`
  - `astart`
  - `astop`
  - `channel`
  - `colormode`
  - `volume`
  - `mute`
- Color modes: `RGB16`, `YCbCr422`, `YCbCr411`.

Key internal pieces:
- `tvinit()` performs PCI discovery, maps registers, detects board/tuner, initializes capture defaults, and enables interrupts.
- `tvinterrupt()` handles video and audio RISC interrupts, errors, and block/frame advancement.
- `riscpacked()`, `riscplanar411()`, `riscplanar422()`, and `riscaudio()` generate hardware DMA instruction streams.
- `frequency()` tunes channels via tuner I2C commands.
- `mspreset()`, `mspvolume()`, and `msptune()` operate the MSP audio chip through bit-banged I2C.
- `kfirinitialize()` loads and resets the Hauppauge KFIR path.

Research notes:
- `video` reads return the last DMA-completed frame.
- `audio` reads track a per-open block cursor through `c->aux`.
- `regs` dumps Bt848 and optional Bt878 register windows.
- Lifetimes for video and audio buffers are guarded by reference counts to prevent stop/free while reads are active.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devtv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devusb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devusb.c

Read completely: 1474 lines.

This file implements the generic Plan 9 USB device framework, exposed as `#u`.

Key behavior:
- Maintains host-controller instances, USB devices, and endpoints.
- Creates root hub endpoint zero for every detected HCI.
- Exposes `#u/usb/ctl` plus dynamic endpoint directories `epN.M`.
- Each endpoint directory contains `data` and `ctl`.
- Allows endpoint aliases at top-level `#u` through the `name` endpoint control.
- User-space enumeration is expected; this kernel driver provides endpoint creation, configuration, and I/O routing.
- Controller-specific behavior is delegated through `Hci` methods from UHCI/OHCI/EHCI drivers.

Important interfaces:
- Device name: `usb`, rune `L'u'`.
- Global control commands: `debug`, `dump`.
- Endpoint control commands include:
  - `new`
  - `newdev`
  - `hub`
  - `speed`
  - `maxpkt`
  - `ntds`
  - `pollival`
  - `samplesz`
  - `hz`
  - `info`
  - `detach`
  - `address`
  - `debug`
  - `clrhalt`
  - `name`
  - `timeout`
  - `reset`

Key internal pieces:
- `addhcitype()` registers HCI driver reset functions.
- `usbreset()` probes configured and auto-detected HCIs.
- `usbinit()` creates root hubs.
- `epalloc()`, `getep()`, and `putep()` manage endpoint lifetime.
- `newdev()` creates endpoint zero and device state.
- `newdevep()` creates non-zero endpoints for a device.
- `rhubread()` and `rhubwrite()` emulate minimal root-hub class requests.
- `usbload()` estimates periodic endpoint bandwidth cost.

Research notes:
- Data files are exclusive-use and enforce endpoint direction.
- Endpoint configuration generally must happen before opening the data file.
- Detached devices transition to `Ddetach` and release endpoint filesystem references.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devvga.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devvga.c

Read completely: 500 lines.

This file implements the Plan 9 VGA control device `#v`.

Key behavior:
- Reserves standard VGA I/O register ranges.
- Exposes VGA BIOS memory, screen control, and optional overlay interfaces.
- `vgactl` accepts commands to select VGA driver, cursor mode, screen size, palette depth, blanking, panning, hardware acceleration, and linear aperture setup.
- `vgabios` reads from low physical address space via `kaddr(0)`.
- Overlay operations dispatch through the active `VGAdev`.

Important interfaces:
- Device name: `vga`, rune `'v'`.
- Files:
  - `vgabios`
  - `vgactl`
  - `vgaovl`
  - `vgaovlctl`
- Uses global screen state from `screen.h`, including `vgascreen`, `physgscreenr`, `blanktime`, `hwaccel`, `hwblank`, and `panning`.

Research notes:
- `checkport()` allows VGA standard ports and otherwise requires unused I/O ranges.
- `CMsize` validates draw channel/depth consistency before resizing screen image state.
- Overlay control sends synthetic `openctl` and `closectl` messages to the active VGA device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devvga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/dma.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/dma.c

Read completely: 264 lines.

This file implements support routines for the i8237 ISA DMA controllers.

Key behavior:
- Defines two DMA controller port maps and per-channel transfer state.
- Allocates low-memory bounce buffers below 16 MB for ISA DMA.
- `dmainit()` reserves DMA controller I/O ports and assigns a bounce buffer to a channel.
- `dmasetup()` programs DMA controller address, page, count, and mode registers.
- Uses bounce buffers when memory is user-space, crosses a 64 KB boundary, or is above 16 MB.
- `dmadone()` checks terminal count status.
- `dmaend()` disables the channel and copies read data out of the bounce buffer when needed.

Important interfaces:
- Public functions: `_i8237alloc`, `dmainit`, `dmasetup`, `dmadone`, `dmaend`.
- Uses `xspanalloc()`, `PADDR()`, `ioalloc()`, `outb/inb`, and interrupt locks.

Research notes:
- Maximum transfer is clamped to 64 KB.
- 16-bit DMA channels use `shift = 1`, affecting address/count programming.
- The commented `dmacount()` helper is present but disabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether2000.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether2000.c

Read completely: 236 lines.

This file implements NE2000-compatible Ethernet support on top of the shared DP8390 driver.

Key behavior:
- Supports PCI NE2000-style adapters including Realtek 8029 and Winbond 89C940.
- Builds a controller list by scanning PCI Ethernet-class devices.
- Matches by known PCI IDs or an explicit `id=` option.
- Configures DP8390 parameters for NE2000 data/reset ports.
- Reads PROM through DP8390 remote DMA to validate marker bytes and obtain MAC address.
- Registers as `NE2000`.

Important interfaces:
- Link function: `ether2000link()`.
- Reset hook: `ne2000reset()`.
- Uses `etherif.h` and `ether8390.h`.
- Calls `dp8390reset()`, `dp8390read()`, and `dp8390setea()`.

Research notes:
- Defaults are `irq=2`, packet memory offset `0x4000`, and size `16 KB` when unspecified.
- `nodummyrr` option disables dummy remote reads.
- If PROM validation fails, the I/O range and allocated DP8390 state are released.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether2000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether2114x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether2114x.c

Read completely: 1836 lines.

This file implements Ethernet support for DEC Tulip 2114x-family PCI controllers and compatible PNIC/ADMtek variants.

Key behavior:
- Supports 21041, 21140, 21143, PNIC, PNIC-II, ADMtek Centaur-P, and CardBus ADMtek variants.
- Uses descriptor rings for receive and transmit.
- Reads and partially decodes serial ROM media information.
- Handles media selection through compact SROM blocks, MII PHY blocks, and fallback fake leaf data for non-conforming cards.
- Supports explicit medium and full-duplex options.
- Posts a Tulip setup packet to program the station address.
- Adapts transmit threshold after underflow.
- Reports extensive receive/transmit/error counters through `ifstat`.

Important interfaces:
- Link function: `ether2114xlink()`.
- Registered names: `2114x`, `21140`.
- Uses generic `Ether` hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `shutdown`, `multicast`, `promiscuous`.

Key internal pieces:
- `dec2114xpci()` scans PCI devices, maps I/O ports, resets controllers, and reads SROM.
- `srom()` reads EEPROM, locates station address, finds media info leaves, and probes PHYs.
- `media()`, `mediaxx()`, `media21041()`, `type0mode()`, `type2mode()`, `typephymode()`, and `typesymmode()` select and program media modes.
- `ctlrinit()` allocates rings, enables interrupts, starts transmit, and posts setup packet.
- `interrupt()` drains receive descriptors, reclaims transmit descriptors, tracks errors, and handles abnormal interrupts.

Research notes:
- Multicast is effectively always enabled via `Pm`; the multicast callback is a no-op.
- SROM decoding is partial and includes hard-coded leaves for known non-conforming cards.
- PNIC and ADMtek variants have special register handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether2114x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether589.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether589.c

Read completely: 215 lines.

This file implements PCMCIA 3Com 3C589/3C562 Ethernet setup, delegating final operation to the existing EtherLink III driver.

Key behavior:
- Looks for PCMCIA cards whose version string matches `3C589`, `3C562`, or `589E`.
- Claims cards through `pcmspecial()`.
- Configures 3Com ASIC register windows, IRQ routing, transceiver selection, TX/RX reset, and media.
- For 3C562, reads the Ethernet address from tuple `0x88` if the address was not overridden.
- Allows `media=10base2` or `media=10baseT`.
- Falls back from 10BaseT to 10Base2 when autoselect is allowed and link beat is absent.

Important interfaces:
- Link function: `ether589link()`.
- Calls external `etherelnk3reset(Ether*)`.
- Uses `pcmspecial()`, `pcmcistuple()`, and `pcmspecialclose()`.

Research notes:
- Comments state IRQ must be 3 on 3C589/3C562, though the reset function defaults `ether->irq` to 10 before PCMCIA configuration.
- The driver is mostly a PCMCIA/Card Services adapter for the shared 3Com driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether589.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether79c970.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether79c970.c

Read completely: 660 lines.

This file implements Ethernet support for AMD PCnet PCI controllers.

Key behavior:
- Supports AMD 79C970, 79C970A, and 79C973-style PCnet variants.
- Probes PCI vendor/device `0x1022/0x2000`.
- Supports either 16-bit or 32-bit I/O access by probing register behavior.
- Allocates receive and transmit descriptor rings aligned to 16 bytes.
- Builds a PCnet initialization block with MAC address and ring addresses.
- Handles receive and transmit interrupts with descriptor ownership bits.
- Supports promiscuous mode by stopping the chip, changing CSR15, reinitializing rings, and restarting.
- Treats multicast as promiscuous.

Important interfaces:
- Link function: `ether79c970link()`.
- Registered name: `AMD79C970`.
- Generic Ethernet hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, `shutdown`.

Research notes:
- Receive buffers are `ETHERMAXTU + 4` to include CRC.
- Transmit uses queued blocks directly in descriptors.
- Initialization enables the device immediately because VMware’s simulated 79C970 did not restart correctly after an older stop sequence.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether79c970.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8003.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8003.c

Read completely: 273 lines.

This file implements Western Digital/SMC WD8003/8013/8216 Ethernet support using the shared DP8390 core.

Key behavior:
- Defaults to port `0x280`, IRQ `3`, memory `0xD0000`, and size `8 KB`.
- Validates card presence through LAN address ROM checksum.
- Distinguishes old 8003E-style boards, 8013EBT-style boards, 16-bit cards, and 8216 Elite Ultra cards.
- Determines IRQ, memory base, RAM size, and bus width from board registers.
- Enables shared memory and maps interface RAM.
- Configures DP8390 ring layout in shared memory.
- Copies MAC address from ROM unless overridden.
- Claims UMB memory with `umbrwmalloc()`.

Important interfaces:
- Link function: `ether8003link()`.
- Registered name: `WD8003`.
- Uses `ether8390.h` and DP8390 functions.

Research notes:
- `reset8003()` contains several hardware aliasing checks for older cards with limited register sets.
- `reset8216()` uses alternate registers to retrieve memory and IRQ.
- The DP8390 port is at `ether->port + 0x10`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8003.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8139.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8139.c

Read completely: 879 lines.

This file implements Ethernet support for Realtek RTL8139 PCI devices and compatible cards.

Key behavior:
- Supports Realtek RTL8139 plus SMC and D-Link PCI IDs.
- Maintains one large receive ring buffer and four transmit descriptors.
- Handles PCI power-management wake-up and restores BAR/interrupt/cache-line config.
- Initializes MAC address, receive configuration, multicast hash registers, transmit buffers, and interrupts.
- Receives packets by walking the NIC circular receive buffer and copying into Plan 9 `Block`s.
- Transmits directly from aligned blocks or copies unaligned packets into descriptor staging buffers.
- Handles link-speed changes and adjusts output queue limits for 10/100 Mbps.
- Provides `ifstat` output for registers, counters, multicast, alignment, and error state.

Important interfaces:
- Link function: `ether8139link()`.
- Registered name: `rtl8139`.
- Generic Ethernet hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, `shutdown`.

Research notes:
- Receive configuration accepts broadcast, multicast, and physical-match packets.
- Multicast hash uses Ethernet CRC high bits.
- PCIe multicast byte ordering code exists but is disabled by `if (0 && ctlr->pcie)`.
- Serious system errors trigger reinitialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8139.c -->