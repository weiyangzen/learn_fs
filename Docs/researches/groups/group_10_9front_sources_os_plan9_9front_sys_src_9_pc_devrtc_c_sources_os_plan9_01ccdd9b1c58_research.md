# Group Research: group_10_9front_sources_os_plan9_9front_sys_src_9_pc_devrtc_c_sources_os_plan9_01ccdd9b1c58

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devrtc.c

## Purpose
Plan 9 `#r` RTC/NVRAM device for PC CMOS real-time clock hardware at I/O ports `0x70/0x71`. It exposes kernel namespace files for wall-clock seconds and CMOS NVRAM.

## Exposed Interface
- Device table: `rtcdevtab`, device character `r`, name `rtc`.
- Files:
  - `rtc`: readable by all, writable only by `eve`; reads seconds since Unix epoch.
  - `nvram`: accessible only by `eve`; reads/writes 256 bytes of CMOS NVRAM starting at offset 128.
- Helper API exported to other kernel code:
  - `rtctime()`
  - `nvramread(int addr)`
  - `nvramwrite(int addr, uchar data)`

## Implementation Notes
- `rtcinit()` reserves the two CMOS I/O ports via `ioalloc`.
- `_rtctime()` polls RTC update-in-progress status, reads BCD seconds/minutes/hour/day/month/year, converts two-digit years to 1900/2000, then converts to epoch seconds.
- `rtctime()` serializes RTC/NVRAM access with `nvrtlock` and requires two identical successive reads to reduce rollover races.
- `rtcwrite()` accepts a decimal seconds value for `rtc`, converts it to BCD RTC fields, and writes CMOS clock registers.
- Time conversion is self-contained in `rtc2sec()`, `sec2rtc()`, and leap-year tables.

## Filesystem Relevance
This is a Plan 9 kernel device-file implementation: hardware is represented as files under a device namespace rather than as a block filesystem. It is relevant for understanding Plan 9 device/VFS conventions: `Chan`, `Dirtab`, `devwalk`, `devstat`, `devdirread`, `readnum`, and device permission checks.

## Risks / Quirks
- Uses 32-bit `ulong` seconds, so epoch range is limited.
- RTC year pivot assumes `<70` means 2000s and otherwise 1900s.
- NVRAM access is raw and privileged, with minimal validation beyond offset/size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devtv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devtv.c

## Purpose
Plan 9 `#V` TV capture device driver for Brooktree Bt848/Bt878 TV tuner/capture cards, including Hauppauge-specific audio/KFIR support.

## Exposed Interface
- Device table: `tvdevtab`, device character `V`, name `tv`.
- Namespace layout:
  - `#V/tvN/video`: read current captured video frame.
  - `#V/tvN/audio`: read captured audio blocks when Bt878 audio is present.
  - `#V/tvN/ctl`: control commands.
  - `#V/tvN/regs`: dump Bt848/Bt878 MMIO registers.
- Control commands:
  - `vstart <nframes>`
  - `astart <input> <rate> <blocks> <blocksize>`
  - `astop`
  - `vgastart <physaddr> <stride>`
  - `vstop`
  - `channel <channel> <finetune>`
  - `colormode <RGB16|YCbCr422|YCbCr411>`
  - `volume <left> <right>`
  - `mute`

## Implementation Notes
- `tvinit()` scans PCI for Bt848/Bt878 variants, maps MMIO registers, detects boards via I2C EEPROM probes, configures tuner type, initializes capture geometry, interrupt masks, GPIO audio muxing, and optional Bt878 audio path.
- The file contains a register-layout struct `Bt848`, board/tuner tables, Hauppauge EEPROM tuner mapping, audio mux tables, and NTSC geometry constants.
- Video capture is programmed with Bt848 RISC DMA instruction streams:
  - `riscpacked()` for packed RGB16.
  - `riscplanar411()` for planar YCbCr 4:1:1.
  - `riscplanar422()` for planar YCbCr 4:2:2.
- `vstart()` allocates frame buffers and DMA programs, chains frame programs in a ring, and `vactivate()` starts capture.
- `vgastart()` captures directly into a caller-supplied physical framebuffer.
- `vstop()` stops RISC/FIFO/capture and frees frame buffers, refusing while readers hold `fref`.
- Audio capture uses `riscaudio()`, `astart()`, `astop()`, Bt878 audio DMA, and `aref` to prevent freeing buffers during reads.
- `tvinterrupt()` acknowledges video/audio interrupt bits, records last completed video frame, advances audio block counters, wakes audio readers, and resets DMA on selected error conditions.
- I2C support is split between Bt848 hardware I2C operations (`i2cread`, `i2cwrite`) and bit-banged helpers used for MSP3400 audio-chip access.
- MSP3400 support includes reset, register read/write, volume/mute, audio standard autodetection, and status text in `tv->ainfo`.
- Hauppauge KFIR/Altera support loads `hcwAMC` microcode through GPIO and initializes the encoder/control logic.

## Filesystem Relevance
This is a rich Plan 9 device namespace example. It maps a PCI multimedia capture card into files and text commands, showing how Plan 9 drivers expose streaming buffers, register dumps, and mutable control state via `read`/`write` on device files.

## Risks / Quirks
- Several paths use `assert()`/`panic()` on allocation or unsupported board states.
- Audio read logic has debug `print()` calls and unusual block-index arithmetic.
- Capture dimensions are hard-coded to NTSC active geometry.
- Only selected boards/tuners are supported; STB cards explicitly panic.
- The driver directly accepts a physical address for `vgastart`, so correctness depends on trusted privileged use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devtv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devvga.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devvga.c

## Purpose
Plan 9 `#v` VGA controller device exposing a `vgactl` control/status file for screen configuration, hardware cursor, acceleration, framebuffer aperture, and VGA driver selection.

## Exposed Interface
- Device table: `vgadevtab`, device character `v`, name `vga`.
- Files:
  - `vgactl`: read status, write textual control commands.
- Commands include:
  - `type <driver>`
  - `size <WxHxD> <chan>`
  - `actualsize <WxH>`
  - `drawinit`
  - `linear <size> [align]`
  - `hwgc <cursor-driver|off>`
  - `hwaccel on|off`
  - `hwblank on|off`
  - `softscreen on|off`
  - `pcidev <tbdf>`
  - `tilt <mode>`
  - `textmode`

## Implementation Notes
- `vgareset()` reserves standard VGA I/O port ranges and finds the first PCI display device.
- `vgaread()` reports active VGA driver type, configured virtual/actual size, tilt, hardware cursor, acceleration/blanking status, aperture address, and softscreen state.
- `vgactl()` is the command dispatcher. It updates global `vgascreen[0]`, calls driver-specific `enable`, `disable`, and `drawinit` hooks, and coordinates screen-image recreation.
- Screen-changing operations use `drawlock`, `deletescreenimage()`, `setscreensize()`, `setactualsize()`, `vgascreenwin()`, and `resetscreenimage()`.
- Hardware cursor changes call `cursoroff()`/`cursoron()` and cursor-driver hooks.
- `CMlinear` requests a framebuffer aperture with `screenaperture()`.

## Filesystem Relevance
This is a canonical Plan 9 control-file driver: graphics device state is configured by writing command strings to a file, and status is read as text. It is not a filesystem implementation, but it illustrates Plan 9 device-file semantics and user/kernel control-plane design.

## Risks / Quirks
- The driver assumes a single VGA screen at `vgascreen[0]`.
- Several commands require prior screen sizing and fail with `"set the screen size first"`.
- Driver lists are external (`vgadev[]`, `vgacur[]`), so behavior depends on platform-linked VGA modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devvga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devvmx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devvmx.c

## Purpose
Plan 9 `#X` Intel VMX virtualization device. It creates and controls VMX guests through file operations, with guest registers, memory map/EPT configuration, run control, exceptions, interrupts, waits, and floating-point state exposed through a Plan 9 namespace.

## Exposed Interface
- Device table: `vmxdevtab`, device character `X`, name `vmx`.
- Root namespace:
  - `clone`: open by `eve` to create a VM.
  - per-VM directories named by numeric slot.
- Per-VM files:
  - `ctl`: read VM index; write control commands.
  - `regs`: read/write guest registers and VM-exit fields.
  - `status`: read VM state (`init`, `ready`, `running`, `dead`, `ending`).
  - `map`: read/write guest physical memory map backed by global segments and EPT.
  - `wait`: wait for VM exits or IRQ acknowledgements.
  - `fpregs`: read/write saved guest FP state.
- `ctl` commands:
  - `quit`
  - `go [reg=value;...]`
  - `step [reg=value;...]`
  - `stop`
  - `exc <event>`
  - `irq [event]`
  - `extrap <bitmap>`

## Implementation Notes
- Low-level VMX assembly hooks are external: `vmxon`, `vmxoff`, `vmclear`, `vmptrld`, `vmlaunch`, `vmread`, `vmwrite`, `invept`, and `invvpid`.
- `vmxreset()` detects VMX support, verifies BIOS enablement, requires EPT and VPID, and allocates per-CPU `VmxMach` state.
- `vmxstart()` enables VMXE, validates CR0/CR4 fixed bits, performs `VMXON`, creates a VMCS, binds it to the process, and calls `vmcsinit()`.
- `vmcsinit()` initializes VMCS control fields, host state, guest segment/control defaults, EPT pointer, VPID, MSR bitmap/load areas, PAT/EFER handling, FP state, TSC offset, and 64-bit syscall MSR handling.
- `guestregs[]` maps readable/writable textual register names to VMCS fields or `Vmx` struct fields. Special writers enforce kernel-reserved CR0/CR4 bits and update IA32_EFER long-mode-active state.
- EPT mapping:
  - `eptwalk()` lazily allocates EPT page-table pages.
  - `epttranslate()` maps guest physical pages to Plan 9 segment pages or clears mappings.
  - `cmdsetmeminfo()` parses map lines of access flags, memory type, guest range, segment name, and offset.
  - `cmdgetmeminfo()` formats current memory mappings.
  - `cmdclearmeminfo()` frees EPT tables and mapping metadata.
- VM command execution is serialized through `VmCmd` queues. `vmxcmd()` sends commands to the VM kproc and sleeps for completion.
- `vmxproc()` is the per-VM kernel process. It wires itself to a CPU, initializes VMX, processes commands, injects pending exceptions/IRQs, flushes VPID/EPT when needed, restores guest FP/debug/control state, launches/resumes the guest, saves state on VM exit, and records exit status.
- `cmdwait()` formats VM exits using `exitreasons[]` and `except[]`, including qualification, PC/SP, instruction length/info, exception code, guest virtual/physical addresses, and AX for I/O exits.
- `cmdquit()` tears down mappings, clears VMCS, performs `VMXOFF` when the CPU has no remaining VMs, removes the VM table entry, frees the `Vmx`, and exits the kproc.
- `vmxshutdown()` iterates all VMs and issues `quit`.
- Namespace functions (`vmxgen`, `vmxwalk`, `vmxstat`, `vmxopen`, `vmxread`, `vmxwrite`, `vmxremove`, `vmxclose`) implement Plan 9 file semantics and privilege checks.

## Filesystem Relevance
This is highly relevant to virtualization/block-device integration in subset A even though it is not a filesystem. It presents a VM control API as a filesystem-like namespace, and its `map` file binds guest physical memory to Plan 9 segments through EPT mappings.

## Risks / Quirks
- Access is restricted to `eve` for non-directory VM files and clone creation.
- The `cmdsetfpregs()` bounds adjustment appears suspicious: `n = sizeof(FPsave) - n` when `off + n` exceeds the buffer likely should account for `off`.
- VMX correctness depends on CPU-specific MSR control bits and external assembly routines.
- EPT mappings assume fixed/sticky segments and directly index segment maps/pages.
- `go`/`step` use textual inline register assignments, so malformed control input is rejected at command execution time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devvmx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/dma.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/dma.c

## Purpose
PC i8237 DMA controller support with bounce buffers for ISA-style DMA channels that must operate below 16 MiB and cannot cross 64 KiB boundaries.

## Exposed Interface
- `_i8237alloc()`
- `dmainit(int chan, int maxtransfer)`
- `dmabva(int chan)`
- `dmacount(int chan)`
- `dmasetup(int chan, void *va, long len, int flags)`
- `dmadone(int chan)`
- `dmaend(int chan)`

## Implementation Notes
- Defines two DMA controller port maps (`dma[0]`, `dma[1]`) with address/count/page/mode/mask registers and a `shift` for 8-bit vs 16-bit channels.
- `_i8237alloc()` allocates one or two 64 KiB bounce buffers aligned to 64 KiB and below 16 MiB, depending on global `i8237dma`.
- `dmainit()` reserves DMA I/O ports once and assigns a preallocated bounce buffer to a channel.
- `dmasetup()` decides whether a transfer can use the caller buffer directly. It falls back to the channel bounce buffer if:
  - address is not kernel memory,
  - physical range crosses a 64 KiB boundary,
  - physical address is at or above 16 MiB.
- Non-read DMA copies outbound data into the bounce buffer before programming the controller.
- Programming the DMA address, count, page, mode, and mask is done under the controller lock.
- `dmaend()` masks the channel and copies read data from the bounce buffer back to the original destination.

## Filesystem Relevance
Not a filesystem component, but part of the PC kernel device substrate used by legacy storage/network drivers. Important for understanding older block/storage device DMA constraints in Plan 9.

## Risks / Quirks
- Bounce buffers are allocated early and fixed; exhaustion produces `"no i8237 DMA bounce buffer < 16MB"`.
- Maximum transfer is capped at 64 KiB.
- `dmacount()` reads low/high count bytes and adjusts for controller word size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ec.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ec.c

## Purpose
Embedded Controller access helper for ACPI-style laptop ECs, typically using command/status port `0x66` and data port `0x62`.

## Exposed Interface
- Kernel helper API:
  - `ecread(uchar addr)`
  - `ecwrite(uchar addr, uchar val)`
  - `ecinit(int cmdport, int dataport)`
- Adds an architecture file:
  - `ec`: 256-byte read/write view of EC address space.

## Implementation Notes
- Maintains global EC state with initialization flag and two ports (`EC_SC`, `EC_DATA`).
- `ecwait()` polls status bits with a timeout and logs status/caller PC on timeout.
- `ecread()` waits for input buffer clear, sends `RD_EC`, writes address, waits for output buffer full, reads data, and waits for output buffer clear.
- `ecwrite()` waits for input buffer clear, sends `WR_EC`, writes address and value, and waits for completion after each stage.
- `ecarchread()` and `ecarchwrite()` expose byte-range reads/writes through `addarchfile`.
- `ecinit()` reserves both I/O ports and registers the arch file.

## Filesystem Relevance
This is a small Plan 9 arch-file bridge from hardware EC address space to a file-like kernel interface. It demonstrates device namespace exposure through `addarchfile` rather than a full `Dev` table.

## Risks / Quirks
- Timeout loop is fixed at 1000 iterations with 1 ms delay.
- No EC burst mode or query command support is exposed despite constants being defined.
- The arch file permits raw EC writes and is therefore privileged by mode `0660`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether2000.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether2000.c

## Purpose
NE2000-compatible Ethernet driver glue for DP8390-based PCI/ISA adapters, including Realtek 8029 and Winbond 89C940 PCI variants.

## Exposed Interface
- Link function: `ether2000link()`
- Registers Ethernet card type:
  - `addethercard("ne2000", ne2000reset)`

## Implementation Notes
- Uses common DP8390 support from `ether8390.h`.
- PCI discovery builds a list of Ethernet-class PCI devices and matches known IDs or a user-specified `id=` option.
- `ne2000reset()` sets default IRQ/memory/size values, reserves I/O space, allocates a `Dp8390`, configures data port and ring offsets, resets the board through the NE2000 reset port, and probes PROM marker bytes.
- Reads the PROM through DP8390 remote DMA, validates marker bytes (`0x57` patterns, with a Parallels exception), and copies the station address unless already overridden.
- Calls `dp8390reset()` and `dp8390setea()` to initialize the shared 8390 core.

## Filesystem Relevance
This is a network device driver, not filesystem code. It is relevant to Plan 9 kernel device infrastructure and the generic `Ether` registration model that exposes network interfaces elsewhere in the OS.

## Risks / Quirks
- Old NE2000 assumptions: default IRQ 2, memory base `0x4000`, size 16 KiB.
- Supports unknown PCI IDs only through explicit `id=` option.
- Failed PROM validation frees resources and rejects the device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether2000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether2114x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether2114x.c

## Purpose
DEC 2114x/Tulip-family PCI Fast Ethernet driver covering Digital 21041/21140/21143, Lite-On PNIC/PNIC-II, and ADMtek Centaur variants.

## Exposed Interface
- Link function: `ether2114xlink()`
- Registers Ethernet card types:
  - `addethercard("2114x", reset)`
  - `addethercard("21140", reset)`

## Implementation Notes
- Implements descriptor-ring transmit/receive with 64 RX descriptors and 64 TX descriptors.
- `dec2114xpci()` scans PCI Ethernet devices, filters supported IDs, reserves I/O ports, exits 21143 sleep mode when needed, resets hardware, decodes SROM, and builds a controller list.
- `srom()` reads serial ROM, identifies MAC address layout, fabricates SROM leaves for PNIC/ADMtek, parses media info blocks, tracks selected connection type, and scans MII PHYs for type 1/3 blocks.
- Media handling is the core complexity:
  - `media21041()` handles 21041 media programming.
  - `mediaxx()` dispatches compact/extended SROM media blocks.
  - `type0mode()`, `type2mode()`, `typesymmode()`, `typephymode()`, and `typephylink()` program CSR6/CSR12-15 or MII PHYs for selected media.
  - User options can force half/full duplex or a named medium from `mediatable`.
- `ctlrinit()` allocates RX/TX rings, initializes descriptors, enables interrupts, starts transmit state, builds a setup packet for the station address, and opens the output queue.
- `interrupt()` handles normal/abnormal interrupts, receives packets, records RX/TX errors, frees transmitted buffers, tops up TX, and raises TX threshold after underflow.
- `txstart()` sends either pending setup packet or queued data blocks and kicks the NIC.
- `ifstat()` exports counters and an SROM dump.
- `promiscuous()` toggles CSR6 promiscuous mode; multicast is always accepted via `Pm`.

## Filesystem Relevance
Network driver only, but useful for kernel substrate research: it shows PCI enumeration, EEPROM parsing, media negotiation, DMA ring ownership, and Plan 9 `Ether` integration.

## Risks / Quirks
- Comments list incomplete work: thresholds, ring sizing, fuller error handling, setup packet cleanup, attach-time initialization, and full SROM decoding.
- Some media paths contain guessed or special-case programming for old hardware.
- `interrupt()` panics on unhandled status bits.
- Shutdown prints and performs a software reset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether2114x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether589.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether589.c

## Purpose
3Com 3C589/3C562/589E PCMCIA Ethernet setup wrapper using the shared EtherLink III reset path.

## Exposed Interface
- Link function: `ether589link()`
- Registers:
  - `addethercard("3C589", reset)`
  - `addethercard("3C562", reset)`
  - `addethercard("589E", reset)`

## Implementation Notes
- Defines command/status registers and selected windowed 3Com registers.
- Uses `pcmspecial()` to locate a supported PCMCIA card.
- Defaults IRQ to 10 and I/O port to `0x240` if unspecified.
- For 3C562, reads the Ethernet address from CIS tuple `0x88` if the user did not override it, swapping byte pairs.
- Parses `media=10base2` or `media=10baseT`.
- `configASIC()` selects window 0, enables config, forces IRQ resource config, programs transceiver selection, resets TX/RX, then calls external `etherelnk3reset()`.
- Reset tries 10BaseT first when allowed, checks link beat, and falls back to 10Base2 when allowed.

## Filesystem Relevance
Network driver setup code only. Relevant as a compact example of Plan 9’s Ethernet-card registration and PCMCIA-specific hardware configuration.

## Risks / Quirks
- Comment notes 10Base2 path needs checking.
- 3C589/3C562 IRQ is effectively forced through resource config.
- Fallback media detection is simple and link-beat dependent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether589.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether79c970.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether79c970.c

## Purpose
AMD PCnet PCI Ethernet driver for AMD79C970/79C970A/79C973-class devices, including VMware-emulated PCnet variants.

## Exposed Interface
- Link function: `ether79c970link()`
- Registers:
  - `addethercard("AMD79C970", reset)`

## Implementation Notes
- Uses receive and transmit descriptor rings:
  - RX ring: 64 descriptors.
  - TX ring: 16 descriptors.
- Supports both 16-bit and 32-bit I/O styles by probing RAP/RDP behavior after reset.
- `amd79c970pci()` finds PCI vendor/device `0x1022/0x2000`, reserves ports, and builds a controller list.
- `reset()` selects an inactive controller, enables PCI bus mastering, identifies chip version through CSR88/CSR89, reads station address from APROM unless overridden, and adjusts reported speed for VMware MAC OUIs.
- `ringinit()` allocates aligned descriptor rings and RX buffers, resets TX/RX indices, and prepares descriptors.
- Initializes the PCnet initialization block with ring lengths, MAC address, ring physical addresses, and points CSR1/CSR2 at it.
- Enables auto-padding in CSR4 and sets PCnet-PCI software style through BCR20.
- `interrupt()` acknowledges interrupts, records memory/missed/babble errors, processes RX descriptors into `etheriq()`, records RX/TX error counters, frees completed TX blocks, and restarts transmit.
- `promiscuous()` stops the chip, modifies CSR15, reinitializes rings, and restarts.
- `ifstat()` exports detailed RX/TX/chip error counters.

## Filesystem Relevance
Network driver only. It illustrates DMA descriptor-ring handling and Plan 9 generic Ethernet hooks (`attach`, `transmit`, `promiscuous`, `multicast`, `ifstat`).

## Risks / Quirks
- Header says “finish this rewrite”.
- Busy-waits on initialization completion.
- Promiscuous reconfiguration waits for all queued TX descriptors to drain.
- VMware-specific speed inference is based on MAC prefix, not negotiated link state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether79c970.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8003.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8003.c

## Purpose
Western Digital/SMC WD8003/WD8013 and SMC 8216 Ethernet driver using the shared DP8390 core.

## Exposed Interface
- Link function: `ether8003link()`
- Registers:
  - `addethercard("WD8003", reset)`

## Implementation Notes
- Handles 83C584 bus interface registers, old “dumb” 8003E aliasing behavior, 16-bit card detection, and 8216 alternate register set.
- `reset()` sets defaults (`port=0x280`, `irq=3`, `mem=0xD0000`, `size=8KiB`), reserves I/O ports, reads LAN address ROM, validates checksum, allocates `Dp8390`, and dispatches to `reset8003()` or `reset8216()`.
- `reset8003()` detects cards without a full interface chip, derives memory/IRQ/width, detects 16-bit operation, enables interface RAM, and sets LAN/memory width bits.
- `reset8216()` reads memory/IRQ settings through alternate registers, enables RAM/interrupts, and forces 16-bit width.
- Sets DP8390 ring pages, calls `dp8390reset()`, copies station address if not overridden, and calls `dp8390setea()`.
- Claims upper memory block with `umballoc()` and warns if unavailable.

## Filesystem Relevance
Network driver only. Relevant to low-level PC memory/I/O resource handling and legacy NIC shared-memory buffer setup, which resembles old block-device memory window constraints.

## Risks / Quirks
- Many compatibility paths for old cards rely on register aliasing/probing.
- Default memory/IRQ assumptions target old ISA hardware.
- Failure to reserve UMB memory only logs a warning after hardware init.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8003.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8139.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8139.c

## Purpose
Realtek RTL8139 PCI Fast Ethernet driver, excluding RTL8129.

## Exposed Interface
- Link function: `ether8139link()`
- Registers:
  - `addethercard("rtl8139", rtl8139pnp)`

## Implementation Notes
- PCI probe supports Realtek 8139 and several compatible board IDs, plus user-specified `id=`.
- `rtl8139pnp()` builds an Ethernet-controller PCI list, matches a controller, fills `Ether` fields, reads station address if not overridden, installs hooks, and enables interrupts.
- `rtl8139attach()` lazily allocates RX buffer and four transmit buffers, then calls `rtl8139init()`.
- `rtl8139init()` resets/halt state, writes MAC address, initializes ring receive buffer, configures RX/TX DMA, interrupts, multicast hash registers, and enables TX/RX.
- RX model is the RTL8139 contiguous ring buffer:
  - `rtl8139receive()` tracks CAPR/CBR, handles wrap-around, copies packets to new `Block`s, strips CRC, and resets receiver on packet-status errors.
- TX model has four descriptors:
  - `rtl8139txstart()` queues blocks into descriptors, copying unaligned packets to aligned per-descriptor buffers.
  - `rtl8139interrupt()` frees completed descriptors, raises early-TX threshold on underrun, and restarts queueing.
- `rtl8139multicast()` computes Ethernet CRC hash and writes multicast filter registers.
- `rtl8139promiscuous()` toggles accept-all in RCR.
- `rtl8139stat()` reports configuration, counters, PHY/media registers, and alignment statistics.
- Link-change interrupt updates speed based on media status.

## Filesystem Relevance
Network driver only. It is useful for Plan 9 kernel networking and DMA ring-buffer patterns, not filesystem behavior directly.

## Risks / Quirks
- Receive errors trigger partial receiver reset and may need multicast state restoration per comment.
- PCIe variant multicast byte order branch is compiled out (`if (0 && ctlr->pcie)`).
- Static speed detection is minimal and mostly interrupt-driven thereafter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8139.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8169.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8169.c

## Purpose
Realtek RTL8169/8110/8168/8111/810x PCI/PCIe Gigabit/Fast Ethernet driver with MII support, descriptor rings, checksum flags, and hardware tally counters.

## Exposed Interface
- Link function: `ether8169link()`
- Registers:
  - `addethercard("rtl8169", rtl8169pnp)`

## Implementation Notes
- Supports multiple PCI IDs and many MAC hardware versions (`Macv01` through newer variants such as `Macv51`).
- `rtl8169pci()` scans PCI Ethernet devices, filters supported IDs, reserves I/O BARs, enables PCI, vets MAC version through TCR, halts the chip, and builds a controller list.
- `rtl8169pnp()` selects an inactive controller, fills `Ether` fields, reads MAC address if not overridden, installs hooks, and records initial link state.
- `rtl8169attach()` lazily allocates TX/RX rings, block arrays, and a 64-byte-aligned tally-counter block, enables bus mastering, registers interrupts, initializes hardware, initializes MII/PHY, and starts a reset helper kproc.
- Ring layout:
  - TX ring: 64 descriptors.
  - RX ring: 256 descriptors.
  - RX buffers allocated from a `Bpool` sized to rounded Ethernet MTU plus CRC.
- `rtl8169init()` resets the chip, clears/free old descriptors, replenishes RX buffers, configures C+ mode, descriptor base addresses, tally counters, TX/RX configuration, multicast hash, maximum packet size, coalescing, interrupt mask, and controller-specific RXDV gating.
- `rtl8169mii()` installs MII read/write callbacks using `Phyar`, wakes selected PHYs, obtains PHY revision, prints PHY/MAC info, resets PHY, and starts autonegotiation.
- `rtl8169transmit()` reclaims completed TX descriptors, queues blocks from `edev->oq`, writes descriptor physical addresses, marks ownership, and polls normal-priority queue.
- `rtl8169receive()` processes owned-back RX descriptors, replenishes low rings, validates first/last/error bits, strips CRC, records multicast/FIFO/checksum status, marks `Block` checksum flags, and passes packets to `etheriq()`.
- `rtl8169interrupt()` acknowledges ISR, records serious and recoverable interrupt counters, restarts on system/FIFO errors, processes RX/TX, and updates link on `Punlc`.
- `rtl8169ifstat()` dumps hardware tally counters through DMA, updates generic `Ether` counters, reports driver counters, and prints MII registers.
- `rtl8169multicast()` uses Ethernet CRC hash and reverses hash register byte order for PCIe variants.
- `rtl8169shutdown()` halts the controller.

## Filesystem Relevance
Network driver only, but it is a substantial PCI DMA descriptor-ring implementation. It is useful context for block/storage-style DMA patterns and Plan 9 device-driver resource management.

## Risks / Quirks
- Header notes undocumented “magic” register values and limited tuning/testing.
- Serious errors wake a reset kproc rather than fully recovering inline.
- Hardware-version handling is extensive and may reject unknown versions.
- `rtl8169ifstat()` can raise `Eio` if tally-counter DMA does not complete.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8169.c -->