# Group Research: group_19_9front_sources_os_plan9_9front_sys_src_9_pc_vgat2r4_c_sources_os_plan_563011ed5298

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgat2r4.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgat2r4.c

Plan 9 VGA driver support for the Number Nine Ticket to Ride IV controller. It maps the device MMIO BAR, exposes framebuffer/MMIO VGA segments, implements hardware cursor support, and hooks accelerated rectangle fill/scroll operations into `VGAscr`.

Key behavior:
- `t2r4enable` maps PCI BAR 4 as MMIO, records `scr->mmio`, calls `vgalinearpci`, and exports `t2r4mmio` / `t2r4screen` VGA segments.
- Indexed register helpers `t2r4xi` and `t2r4xo` write low/high index registers then read/write the indexed data register.
- Cursor support programs cursor RAM, cursor colors, hot spot, position, and sync/enable bits. The cursor is translated from Plan 9 `Cursor` masks into the card’s 2-bit-per-pixel cursor format.
- Drawing acceleration initializes destination/source pitch and format for `RGB15`, `RGB16`, and `XRGB32`, then installs `scr->fill`, `scr->scroll`, and `scr->blank`.
- `t2r4hwscroll` emits a bitblt with direction control for overlapping source/destination rectangles, with explicit bailouts for small horizontal copies on known problematic SGI flat panel setups.
- `t2r4hwfill` emits a foreground-color bitblt fill, and `t2r4blank` manipulates cursor/sync control bits to force sync-low blanking.

Notable dependencies:
- Plan 9 PC kernel VGA infrastructure: `screen.h`, `VGAscr`, `VGAdev`, `VGAcur`, `vgalinearpci`, `addvgaseg`.
- PCI and VM mapping helpers: `Pcidev`, `vmap`.
- Draw cursor types and pixel channel constants.

Research notes:
- The file is self-contained hardware register programming; it assumes `scr->pci` is already matched to the target device.
- Busy waits have fixed million-iteration cutoffs and only print diagnostic messages on timeout; callers still continue after timeout.
- Hardware acceleration is disabled for unsupported color channels by clearing `scr->fill` and `scr->scroll`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgat2r4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgatvp3020.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgatvp3020.c

Hardware cursor support for the TI TVP3020 Viewpoint video palette, assumed to be attached to an S3 86C928 VGA controller.

Key behavior:
- Uses CRTC register `0x55` to select the upper indirect DAC address bits, then uses standard VGA palette ports for TVP3020 indexed register access.
- `tvp3020disable` clears cursor enable, Bt485-compatible cursor control, and S3 external hardware cursor mode bits.
- `tvp3020enable` initializes cursor control, sets overscan and cursor colors, and enables the S3 external cursor path.
- `tvp3020load` writes the Plan 9 16x16 cursor into a 64x64 hardware cursor RAM area, padding the rest with transparent pixels.
- `tvp3020move` updates low/high cursor X/Y position registers.

Notable dependencies:
- VGA indexed I/O helpers `vgaxi`, `vgaxo`, `vgao`.
- VGA palette register constants and `Cursor` masks from the PC screen subsystem.

Research notes:
- The cursor data conversion is explicit and bit-order-sensitive: each byte encodes four 2-bit cursor pixels.
- The driver only exports `VGAcur vgatvp3020cur`; it does not provide a full `VGAdev` framebuffer or mode-setting driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgatvp3020.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgatvp3026.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgatvp3026.c

Hardware cursor support for the TI TVP3026 Viewpoint video palette, assumed to be attached to an S3 Vision968 controller.

Key behavior:
- Provides indirect DAC register access through CRTC register `0x55`, similar to the TVP3020 path but with TVP3026-specific direct cursor registers.
- Initializes cursor color table entries and cursor control registers.
- Converts Plan 9 cursor `clr` and `set` bitmaps into the TVP3026 two-plane cursor RAM representation.
- Programs cursor hot spot and low/high X/Y screen coordinates.
- Exports a `VGAcur` implementation for enable, disable, load, and move operations.

Notable dependencies:
- Shared VGA register I/O helpers and cursor definitions.
- S3-specific CRTC control bits for external DAC cursor operation.

Research notes:
- Like `vgatvp3020.c`, this is a DAC cursor shim rather than a full graphics device.
- It assumes the surrounding VGA driver has already selected compatible S3 hardware and DAC routing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgatvp3026.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgavesa.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgavesa.c

VESA BIOS Extensions framebuffer support for the PC kernel VGA layer. It uses `/dev/realmode` and `/dev/realmodemem` to call VBE interrupt `0x10`, validates the current VBE mode, derives framebuffer geometry, and registers a linear framebuffer mapping.

Key behavior:
- Defines a 32-bit real-mode `Ureg386` interface and a shared mode-info buffer at `RealModeBuf`.
- `vbesetup` prepares BIOS register state and clears the mode buffer.
- `vbecall` copies mode buffer state into real-mode memory, invokes interrupt `0x10`, checks VBE success status, and reads the mode buffer back.
- `vbecheck`, `vbegetmode`, and `vbemodeinfo` validate VBE 2+ support and fetch the active mode’s mode-info block.
- `vmode` decodes VBE attributes, bytes-per-line, dimensions, depth, physical framebuffer address, and Plan 9 channel string.
- `vesalinear` maps the current linear framebuffer, using PCI BAR containment when possible to size the mapping and falling back to a heuristic if PCI sizing is unavailable.
- `vesablank` uses VBE DPMS function `0x4f10`, with a process alarm guard for kernel processes because some BIOS implementations can hang in blank/unblank calls.
- `vesabootscreenconf` converts bootloader-provided VBE mode info into a `*bootscreen=` configuration line.

Notable dependencies:
- Plan 9 real-mode devices, channel I/O, and error unwinding.
- VGA linear mapping helpers `vgalinearaddr` and `addvgaseg`.
- PCI scanning for framebuffer BAR sizing.

Research notes:
- This driver relies on the BIOS mode already being set; it does not enumerate or select modes.
- The Bochs note explains why the current mode’s linear bit is not trusted strictly.
- The static `creg` and `cmem` channels are global driver state, opened on enable and closed on disable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgavesa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgavmware.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgavmware.c

VMware SVGA framebuffer and acceleration support for the Plan 9 VGA layer. It supports VMware PCI display devices, maps the framebuffer and FIFO MMIO area, and exposes update, copy, fill, and hardware cursor operations.

Key behavior:
- Identifies VMware PCI vendor/device IDs and selects either legacy fixed I/O ports or BAR-derived I/O ports depending on device generation.
- `vmwarelinear` computes framebuffer base from PCI BAR plus `Rfboffset`, maps the framebuffer, maps FIFO MMIO from BAR 2, initializes FIFO control words, and sets `Rconfigdone`.
- `vmfifowr` appends FIFO commands with wraparound and calls `vmwait` when the FIFO is full.
- `vmwareflush` emits `Xupdate` rectangles so VMware updates the visible display.
- Cursor support defines a 16x16 cursor through `Xdefinecursor`, builds AND/XOR masks from Plan 9 cursor data, and controls cursor position/visibility via SVGA registers.
- `vmwarescroll` emits `Xrectcopy`; `vmwarefill` emits `Xrectfill` for version 1 devices.
- `vgavmwaredev` installs linear mapping, draw initialization, and flush hooks; `vgavmwarecur` installs cursor hooks.

Notable dependencies:
- PCI discovery and BAR mapping.
- Port I/O helpers and VGA framebuffer registration.
- VMware SVGA register and FIFO command conventions embedded as local enums.

Research notes:
- The driver uses one global `Vmware` state object, so it is not structured for multiple simultaneous VMware VGA devices.
- FIFO waits are synchronous and busy-spin on `Rbusy`.
- Fill acceleration is deliberately limited to `vm->ver == 1`; scroll is enabled whenever MMIO is available.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgavmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgax.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgax.c

Shared VGA indexed register access helpers for the PC VGA subsystem.

Key behavior:
- `vgaxi` reads indexed VGA registers for sequencer, CRTC, graphics, and attribute controller ports.
- `vgaxo` writes indexed VGA registers for those same port families.
- Access is serialized with a static interrupt lock because VGA index/data ports are shared mutable state.
- Attribute-controller access handles the VGA flip-flop by reading `Status1` before writes and restores palette access bit `0x20` after palette-index operations.

Notable dependencies:
- Low-level `inb`/`outb` port I/O.
- VGA port constants from `screen.h` / `io.h`.

Research notes:
- The code avoids combined outport writes because some S3 chips have trouble with that for some registers.
- Unknown index port families return `-1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/virtio10pc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/virtio10pc.c

PC-specific VirtIO 1.0 register mapping and typed register I/O helpers.

Key behavior:
- `vin8`, `vin16`, `vin32`, and `vin64` read VirtIO registers through either I/O ports or memory-mapped registers depending on `Vio.type`.
- `vout8`, `vout16`, `vout32`, and `vout64` write through the same abstraction.
- `virtiounmap` releases either an I/O port allocation or a VM mapping.
- `virtiomapregs` decodes a VirtIO PCI capability’s BAR, offset, and length, validates the requested size against the PCI BAR, and maps it as `Vio_port` or `Vio_mem`.

Notable dependencies:
- VirtIO 1.0 definitions from `../port/virtio10.h`.
- PCI config-space helpers and PC I/O allocation/mapping functions.

Research notes:
- 64-bit port I/O is implemented as two 32-bit reads/writes.
- The I/O allocation label is hardcoded as `"ethervirtio10"`, reflecting its likely original network-driver use even though the helper is generic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/virtio10pc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/wavelan.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/wavelan.c

Lucent WaveLAN IEEE 802.11 / Hermes controller driver core for Plan 9 Ethernet integration. It handles register I/O, Hermes command execution, LTV configuration records, transmit/receive framing, stats and scan reports, timer watchdogs, power, attach/detach, control commands, and Ethernet callbacks.

Key behavior:
- CSR helpers support both port-mapped and PCI memory-mapped devices. Memory-mapped Hermes registers are indexed as 16-bit values spaced like 32-bit registers.
- `w_cmd` waits for command readiness, issues Hermes commands, waits for command-complete events, acknowledges them, and validates status.
- `w_seek`, `w_read`, and `w_write` select card buffer IDs and offsets through access channels, then stream words through `WR_Data0` / `WR_Data1`.
- LTV helpers read and write Lucent Length-Type-Value records for MAC address, ESSID, port type, WEP keys, channel, power management, transmit rate, stats, and scan results.
- `w_enable` initializes the card, applies controller options, programs MAC address and WEP state, enables the controller, allocates transmit frame buffers, and enables interrupts.
- `w_rxdone` reads a received Hermes frame, translates 802.11/RFC1042/SNAP or 802.3 payloads into Ethernet blocks, queues them with `etheriq`, and updates signal/noise smoothing.
- `w_txstart` pulls from the Ethernet output queue, constructs either RFC1042/SNAP or 802.3 transmit headers, writes frame data into the card, and starts transmit/reclaim.
- `w_intr` handles RX, TX, allocation, info, TX error, and info-drop events under the controller lock, then tries to continue queued transmit.
- `w_timer` periodically polls missed events, handles transmit watchdog recovery, requests card stats, and triggers base-station scans.
- `w_ifstat` reports driver counters, card status, association info, WEP state, and accumulated hardware stats.
- `w_option` parses control commands for ESSID, station name, channel, mode, IBSS, WEP encryption, clear-packet exclusion, keys, transmit key, and power management.
- `wavelanreset` initializes default controller state, reads the station MAC, wires Ethernet callbacks, and registers the interrupt handler.

Notable dependencies:
- `wavelan.h` for Hermes register constants, LTV types, frame layout, and `Ctlr`.
- Plan 9 Ethernet interfaces: `netif.h`, `etherif.h`, `Ether`, `Etherpkt`, queues, scan readers.
- Kernel block allocation and interrupt primitives.

Research notes:
- The file documents known bugs: endian/alignment/mem-IO concerns, receive watchdog interrupts, power management, multicast filtering, and locking.
- Many low-level routines assume the caller already holds the controller interrupt lock.
- The timer intentionally polls event status because the hardware/driver can miss receive interrupts.
- WEP key support is legacy and hidden in stats output unless `SEEKEYS` is enabled.
- `w_detach` posts a kill note to the timer process and clears `ether->ctlr`, but the timer loop observes that asynchronously.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/wavelan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/wavelan.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/wavelan.h

Shared definitions for the Lucent WaveLAN/Hermes wireless driver.

Key contents:
- LTV type codes for stats, scan, link, port type, MAC, ESSID, channel, AP density, max length, power management, WEP, keys, transmit key, station ID, current network, base station, and tick settings.
- Controller constants for default IRQ/I/O base, I/O window length, command timeout, port modes, transmit rates, key sizes, frame offsets, and Hermes registers/events.
- Hermes command and event bits, frame status values, SNAP header constants, and 802.11/802.3 data offsets.
- Structs:
  - `WStats`: hardware transmit/receive counters.
  - `WScan`: scan result sample with channel, signal/noise, BSSID, beacon interval, capabilities, and SSID.
  - `WFrame`: Hermes frame descriptor and embedded Ethernet/SNAP fields.
  - `WKey`: WEP key length and data.
  - `Wltv`: union-backed Lucent LTV record.
  - `Stats`: driver-side counters and signal/noise state.
  - `Ctlr`: full driver controller state, configuration, TX buffers, WEP state, PCI/MMIO state, and embedded stats.
- Prototypes for WaveLAN CSR access, LTV access, options, attach, interrupt, transmit, status, control, promiscuous/multicast hooks, and reset.

Notable dependencies:
- Plan 9 network constants such as `Eaddrlen`, `Ether`, and `Ureg` are expected from including translation units.
- PCI fields are present but abstracted through `Ctlr`.

Research notes:
- The header mixes hardware protocol, driver state, and exported driver API in one file.
- The `DEBUG` macro is compiled out by default.
- `Ctlr` embeds both `Stats` and `WStats`, making driver and hardware counters directly accessible through a single controller pointer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/wavelan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/yukdump.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/yukdump.h

Debug dump helpers and register tables for a Yukon/Marvell-style Ethernet driver.

Key contents:
- Defines `Regdump` descriptors with register offset, width, and display name.
- Provides register descriptor arrays for PCI registers, GMAC registers, MAC registers, and general device registers.
- `dumppci`, `dumpgmac`, `dumpmac`, and `dumpreg` format hardware register snapshots into a buffer using controller-specific read helpers.
- `optab` and `rs` map descriptor operation codes to short strings.
- `dumpring` summarizes populated ranges in a block ring.
- `descriptorfu` prints detailed transmit/receive descriptor state around the hardware get index for debugging.

Notable dependencies:
- Requires the including Yukon driver to define `Ctlr`, ring types, descriptor/status layouts, register constants, and helper functions such as `gmacread`, `macread32`, `prread16`, and `Pciwaddrl`.

Research notes:
- This is a header containing debug code, not only declarations.
- It is intentionally coupled to one driver’s private data structures and is not a general register-dump facility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/yukdump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/apbootstrap.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/apbootstrap.s

Application Processor bootstrap code for amd64 multiprocessor startup. It is copied below 1MB at `APBOOTSTRAP` and entered by APs in real mode.

Key behavior:
- Starts in 16-bit real mode, normalizes segment registers, loads a temporary GDT, enables protected mode, and far-jumps to 32-bit code.
- 32-bit path loads the AP PML4 physical address, configures CR4 for PAE/PGE, enables long mode through EFER, enables paging/write-protect in CR0, and far-jumps into 64-bit code.
- 64-bit path loads the virtual GDT pointer, clears long-mode-ignored segment registers, clears LDTR, sets `m` and `up`, sets the AP stack from `_apmach`, and calls the C AP startup vector.
- Exposes fixed data slots `_apvector`, `_appml4`, `_apapic`, `_apmach`, and `_apefer` used by `mpstartap`.
- Defines temporary 64-bit and 32-bit descriptors plus physical/virtual GDT pointers.

Notable dependencies:
- Constants from `mem.h`, especially selectors, `KZERO`, `MACHSIZE`, and AP bootstrap address assumptions.
- `squidboy.c` fills the bootstrap data slots before starting the AP.

Research notes:
- The comments note the code is further restricted to the first 64KB due to shortcuts in the real-mode setup.
- It halts forever if the C AP startup vector ever returns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/apbootstrap.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/dat.h

Primary amd64 kernel data-structure header for the 9front PC64 kernel.

Key contents:
- Forward declarations for core kernel, MMU, process, architecture, PCI, PCMCIA, and interrupt structures.
- `Label` scheduler jump context.
- FPU save-state structures for FXSAVE/XSAVE-style state, plus `PFPU` process FPU bookkeeping.
- `Conf` and `Confmem` machine memory/process/image/swap configuration.
- `Segdesc`, `MMU`, and `PMMU` structures for page-table and per-process MMU state.
- Includes `../port/portdat.h`, then defines amd64-specific `Tss`, `Mach`, `PCArch`, CPUID feature bits, MSR numbers, `ISAConf`, global `machp`, register globals `m` and `up`, and `DevConf`.
- `Mach` stores per-CPU scheduler, timing, CPUID, MMU, GDT/TSS, interrupt, FPU, and diagnostic state.
- `PCArch` provides architecture hooks for reset, serial power, NMI, interrupts, clocks, and timers.

Notable dependencies:
- Shared Plan 9 port data model from `portdat.h`.
- `mem.h` constants for CPU counts, page table sizing, and segment selectors.

Research notes:
- This header defines architecture contracts consumed throughout `pc64`.
- It also contains initialized storage for `machp[MAXMACH]`, so it is not purely declarations in the C sense.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/fns.h

Architecture-specific function prototype header for the PC64 kernel.

Key contents:
- Includes shared `portfns.h`, then declares PC64 functions and assembly entry points.
- Covers architecture initialization, boot arguments, CPU identification, clocks, DMA stubs, FPU lifecycle, control/debug register access, I/O port primitives, interrupt/trap entry, MMU mapping, MTRR/PAT, PCI/PCMCIA hooks, process save/restore, real-mode calls, random generation, screen setup, syscall entry, VMX helpers, VM mapping, and reboot/config functions.
- Defines no-op or direct macros for x86-specific behavior: `dmaflush`, `evenaddr`, `kmapinval`, `mmuflushtlb`, `userureg`, `KADDR`, and `PADDR`.
- Declares external function-pointer hooks such as `cycles`, `coherence`, `screenputs`, PCI config accessors, and processor context callbacks.

Notable dependencies:
- Types from `dat.h`, `mem.h`, and shared port headers.

Research notes:
- This is the bridge between C code and the assembly implementations in `l.s`.
- The header centralizes many platform service contracts, so changing prototypes here has broad kernel impact.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/fpu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/fpu.c

amd64 floating-point, SSE, and AVX state management for kernel and user contexts.

Key behavior:
- Selects FPU save/restore backends at CPU initialization: FXSAVE/FXRSTOR or XSAVE/XSAVEOPT/XSAVES when CPUID and `*noavx` allow AVX state.
- `fpinit` initializes x87 control word and MXCSR defaults.
- Trap handlers convert x87/SIMD faults into user notes or kernel panics with decoded exception messages.
- `mathinit` registers math, coprocessor-not-available, coprocessor-overrun, and SIMD trap handlers.
- Uses lazy FPU activation: `mathemu` handles device-not-available traps by allocating/restoring state on first use.
- Process hooks save, restore, fork, clear, and free user FPU state across scheduler and process lifecycle events.
- `fpukenter` and `fpukexit` protect user FPU state and allow kernel code, traps, and interrupts to use floating-point/vector state safely.
- Note handling functions manage nested saved FPU contexts for Plan 9 note delivery.

Notable dependencies:
- Assembly helpers in `l.s`: `_clts`, `_stts`, `_fxsave`, `_fxrstor`, `_xsave`, `_xrstor`, `_xsaveopt`, `_xsaves`, `_fwait`, `_ldmxcsr`.
- Trap registration, process structures, and Plan 9 notes.

Research notes:
- The code maintains separate user and kernel FPU state stacks per process, plus per-machine state for interrupt context.
- Allocation loops can wait for memory when running in process context.
- `fpcheck` intentionally checks pending unmasked exceptions before restoring a saved state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/fpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/l.s

Core amd64 assembly for kernel bootstrap, CPU control, low-level I/O, synchronization, FPU instructions, random instructions, VMX instructions, syscall/trap entry, and interrupt vectors.

Key behavior:
- Boot path starts in 32-bit mode, handles multiboot entry, builds initial identity and high-half mappings, enables long mode, jumps to virtual 64-bit kernel space, clears BSS, initializes `m`, and calls `main`.
- Defines bootstrap GDT descriptors and GDT pointer records for protected and long mode.
- Implements port I/O helpers (`inb`, `ins`, `inl`, `outb`, `outs`, etc.), descriptor table loads, task register load, control register access, XCR access, MSR read/write, cache/TLB instructions, memory fences, and timestamp counter read.
- Implements interrupt priority helpers `splhi`, `spllo`, `splx`, `islo`, atomic test-and-set, compare-and-swap, and scheduler label save/restore.
- Provides FPU/SIMD instruction wrappers used by `fpu.c`.
- Provides RDRAND helpers and buffer filling.
- Provides debug-register and VMX instruction wrappers with shared error-return paths.
- Implements transition to user mode, syscall entry, fork return, interrupt common entry, note return, and interrupt restore.
- Generates the interrupt vector table stubs used by `trapinit0`.

Notable dependencies:
- Register conventions from `mem.h`, especially `RMACH` and `RUSER`.
- C trap/syscall handlers and kernel globals such as `m`, `up`, `main`, `trap`, `syscall`, and `noteret`.

Research notes:
- Several fault-sensitive instruction wrappers expose labels (`_rdmsrinst`, `_wrmsrinst`, `_peekinst`) that `trap.c` recognizes to recover from expected faults.
- This file is central to ABI correctness: stack layout and saved register order must match `Ureg` and syscall/trap C code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/main.c

Main PC64 kernel bootstrap, machine initialization, configuration sizing, first user process entry, and reboot support.

Key behavior:
- Defines global `Conf conf` and `idle_spin`.
- `confinit` derives process/image/swap counts, user/kernel memory split, interrupt allocation budget, and pool maximums from physical memory and boot configuration such as `service`, `*kernelpercent`, and `*imagemaxmb`.
- `machinit` initializes per-CPU `Mach` state while preserving CPU number, PML4, and GDT.
- `mach0init` installs bootstrap CPU `Mach`, PML4, and GDT addresses and marks CPU 0 active.
- `init0` initializes devices, sets kernel environment variables, starts the alarm kproc, builds the initial user stack for `boot`, exits kernel FPU context, and calls `touser`.
- `main` performs the boot sequence: early traps, I/O, console, screen, CPU identification, memory initialization, architecture hooks, allocator setup, traps/math, PCI, MMU, interrupts, timers, processes, devices, pages, first user process, and scheduler.
- Reboot support copies trampoline code to `REBOOTADDR`, adjusts mappings/executable permissions, disables interrupts, and jumps into reboot code to relocate or park.

Notable dependencies:
- Almost every PC64 subsystem: traps, MMU, memory, arch hooks, console, PCI, screen, timers, devices, process setup, and reboot trampoline.
- `rebootcode.i`, generated from `rebootcode.s`.

Research notes:
- Boot order is deliberate: early console/screen precede full MMU and interrupt setup, while process/device setup comes after page and pool initialization.
- Memory pool sizing accounts for large kernel structures but explicitly says mount cache and mount RPC allocations are not included in the estimate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/mem.h

PC64 memory layout, page-table, segment, selector, and low-level machine constants shared by C and assembly.

Key contents:
- Binary size constants (`KiB` through `EiB`), alignment helpers, word/page sizes, page rounding, block/FPU alignment, and CPU/kernel stack sizes.
- Time constants for tick rate and conversion macros.
- User address layout: `UTZERO`, canonical user mask, `USTKTOP`, and user stack size.
- Kernel address layout: high-half `KZERO`, text start `KTZERO`, `VMAP`, `KMAP`, and their sizes.
- Fixed bootstrap physical/virtual addresses for boot args, AP bootstrap, IDT, reboot code, CPU0 PML4/PDP/PD pages, GDT, and `Mach`.
- Segment numbers, selectors, descriptor bit fields, and GDT sizing.
- Virtual and physical MMU constants: PTE map sizes, page-table levels/index macros, PTE flags, no-execute bit, PAT write-combining entry, and page color stub.
- Assembly register aliases for `m` and `up`.

Notable dependencies:
- Used directly by both C and assembly; constants must remain assembler-compatible.

Research notes:
- The file encodes the kernel’s high-half layout and the special early-boot pages assumed by `l.s`, `main.c`, `mmu.c`, and `apbootstrap.s`.
- `PTENOEXEC` depends on `m->havenx`, so it is not a pure constant expression in C use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/mmu.c

amd64 MMU, GDT/TSS setup, kernel mapping hardening, page-table allocation, process address-space switching, temporary mappings, VMAP mappings, PAT write combining, and early page preallocation.

Key behavior:
- Defines base GDT descriptors for kernel/user 64-bit code, user 32-bit code, and user data.
- `mmuinit` removes bootstrap double maps, marks kernel text read-only/non-text no-execute on CPU 0, allocates TSS, installs per-CPU GDT/TSS/IDT, sets GS base to `machp[machno]`, enables syscall MSRs, and points `Lstar` at `syscallentry`.
- `kaddr` and `paddr` validate physical/virtual address conversions.
- `mmualloc` manages per-CPU and global pools of `MMU` page-table descriptors and page-table pages.
- `mmucreate` and `mmuwalk` create or traverse hierarchical page tables for user, KMAP, and VMAP/KZERO addresses.
- `kernelro` splits large pages as needed, clears write permission on kernel text, and sets NX on non-text mappings except AP bootstrap.
- `pmap` and `punmap` create/remove kernel mappings, using 2MB pages when alignment and size permit.
- `mmuzap`, `mmuswitch`, `mmurelease`, and `flushmmu` manage per-process page-table roots and TLB context.
- `putmmu` installs user mappings; `checkmmu` diagnoses mismatches.
- `kmap` and `kunmap` create temporary per-process KMAP mappings for pages not directly reachable through KZERO.
- `vmap` maps physical device memory into the VMAP window as uncached, writable, no-execute; `vunmap` only validates the address.
- `patwc` changes mapped pages to the configured PAT write-combining entry.
- `preallocpages` reserves high memory for `palloc.pages` and the MMU page-table pool before normal page initialization.

Notable dependencies:
- Page constants and selectors from `mem.h`.
- Process `PMMU` fields from `dat.h`.
- Physical allocator and page-cache structures from the port layer.

Research notes:
- VMAP and KZERO PDPs are shared between processors; `vmap` comments explicitly note no synchronization is performed for that shared setup.
- `vunmap` is effectively a validation stub, not an unmapper.
- Kernel hardening relies on NX support through `m->havenx`; without NX, `PTENOEXEC` contributes no bit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/rebootcode.s

Reboot trampoline code copied to low physical memory and executed to relocate or enter a new kernel after paging/long mode teardown.

Key behavior:
- Starts in 64-bit mode with destination, source, and byte count arguments.
- Loads a zero-length IDT and temporary GDT.
- Far-returns into a 32-bit code segment.
- In 32-bit mode, reloads data segments, disables paging, clears CR3, disables long mode in EFER, disables PAE/PGE in CR4, and sets the stack below the target entry.
- If entry is zero, parks the CPU in a halt loop.
- Copies the new kernel image with overlap-safe forward/backward `MOVSB`.
- Jumps to the destination entry point.
- Defines temporary GDT and IDT pointer records.

Notable dependencies:
- Selector and segment constants from `mem.h`.
- `main.c` copies this code to `REBOOTADDR` and jumps to it.

Research notes:
- The trampoline deliberately avoids relying on the existing high-half kernel mapping once paging is disabled.
- The copy logic handles overlapping source/destination ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/squidboy.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/squidboy.c

Multiprocessor AP startup coordinator for the PC64 kernel.

Key behavior:
- `squidboy` is the C entry point called by AP bootstrap assembly. It initializes the AP’s `Mach`, MMU, CPU identity, optional architecture clock, clock synchronization, APIC state, timers, and then enters the scheduler.
- `mpstartap` allocates AP page tables, a GDT page, and a `Mach` structure.
- Builds AP mappings by sharing the kernel high-half and VMAP mappings from CPU 0, plus a low double-map needed by the bootstrap transition.
- Fills the fixed AP bootstrap data slots at `APBOOTSTRAP+0x08` with the C entry vector, PML4 physical address, APIC pointer, `Mach` pointer, and NX/EFER bit.
- Programs the warm-reset vector and CMOS shutdown code, sends the LAPIC startup sequence, waits for the AP to mark itself online, then clears the shutdown code.

Notable dependencies:
- AP bootstrap code in `apbootstrap.s`.
- LAPIC/MP structures and APIC startup helpers.
- `mmuwalk`, `xspanalloc`, and CPU0 page tables.

Research notes:
- The AP shares top-level kernel/VMAP mappings but owns its PML4, low bootstrap mapping, GDT, and `Mach`.
- The code assumes `APBOOTSTRAP` remains in the first 64KB-compatible range; it prints a diagnostic if the warm-reset segment is not zero.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/squidboy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc64/trap.c

amd64 trap, interrupt, syscall, page-fault, notification, register, and debug exception handling.

Key behavior:
- `trapinit0` initializes the IDT at `IDTADDR`, pointing each vector at the assembly vector table and granting user privilege only to breakpoint and syscall vectors.
- `trapinit` initializes IRQ handling, enables NMI, and registers handlers for debug, breakpoint, page fault, double fault, and reserved vector 15.
- `trap` enters kernel context, protects FPU state, dispatches IRQs or user traps, handles recoverable kernel faults from special MSR/peek instruction wrappers, reports unexpected traps, delivers notes, exits kernel context, and restores FPU state.
- `dumpregs`, `callwithureg`, and stack dump helpers print register and stack diagnostics.
- Debug handlers translate hardware watchpoint/debug exceptions and breakpoints into user notes where possible.
- `faultamd64` resolves page faults through the VM fault path, with special handling for kernel faults while copying user memory.
- `syscall` is entered directly from assembly, runs `dosyscall`, arranges `noteret` when notes must be delivered, handles delayed scheduling, and exits kernel/FPU context.
- `notify` and `noted` build and restore user note frames on the user stack.
- `execregs`, `userpc`, `setregisters`, `kprocchild`, `forkchild`, `setkernur`, and `dbgpc` manage user/kernel register contexts.

Notable dependencies:
- Assembly entry/exit paths in `l.s`.
- VM fault handling, notes, process debug locks, and IRQ dispatch.
- Segment selectors and user-address constants from `mem.h`.

Research notes:
- Fault recovery for `_rdmsrinst`, `_wrmsrinst`, and `_peekinst` is coordinated with labels exported by `l.s`.
- `setregisters` masks user-modified segment registers, flags, and PC canonical bits after copying user register state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc64/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/alarm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/alarm.c

Portable process alarm implementation.

Key behavior:
- Maintains a globally sorted linked list of processes with pending alarm times under `alarms`.
- `alarmkproc` runs as a kernel process, walks expired alarms, posts `"alarm"` notes to alive processes, clears their alarm fields, reinserts the first non-expired process, and sleeps until awakened.
- `checkalarms` is called every clock tick on CPU 0 and wakes the alarm process when the head alarm is due or invalid.
- `procalarm` implements alarm setup/cancel for the current process, returns remaining time from the previous alarm, removes any existing alarm entry, and inserts the process in deadline order.

Notable dependencies:
- Process note delivery and `Proc` alarm fields.
- Tick conversion helpers and CPU0 tick count.

Research notes:
- Alarm expiration uses signed subtraction to handle tick wraparound.
- `procalarm(0)` cancels without taking the global alarm lock after computing old remaining time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/alarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/alloc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/alloc.c

Kernel heap/pool allocation wrapper layer.

Key behavior:
- Defines three pools: `mainmem`, `imagmem`, and `secrmem`, each backed by `xalloc`/`xmerge` and protected by pool-specific interrupt locks.
- Pool print/panic callbacks buffer messages while locked and print or panic after releasing the lock.
- `mallocsummary` and `poolsummary` report pool capacity and allocation statistics.
- Implements kernel `smalloc`, `malloc`, `mallocz`, `mallocalign`, `free`, `realloc`, and `msize` on top of pool allocation.
- Maintains two-word allocation padding for malloc/realloc caller tags.
- Implements secret-memory allocation and free through `secrmem`.
- Provides tag setters/getters for allocation diagnostics.

Notable dependencies:
- Generic pool allocator from `<pool.h>`.
- Low-level physical allocation `xalloc` and merging `xmerge`.

Research notes:
- `smalloc` and `secalloc` wait until memory is available; `malloc`/`mallocz` return nil on failure.
- Secret memory uses a distinct pool with `POOL_ANTAGONISM`, but this file only zeroes on allocation, not explicitly on free.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/allocb.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/allocb.c

Network/block buffer allocation helpers for kernel `Block` objects.

Key behavior:
- `_allocb` allocates a `Block` plus headroom, tailroom, and alignment padding, aligns the data area, and initializes read/write pointers with header space reserved.
- `allocb` is process-context allocation that waits for memory and panics if called in interrupt/locked context without memory.
- `iallocb` is interrupt-safe allocation that returns nil on failure, rate-limits warnings, and eventually panics after excessive repeated failures.
- `freeb` returns pooled blocks to their `Bpool` freelist or poisons fields with `Bdead` before freeing ordinary blocks.
- `_alignment` rounds pool alignment to a power of two at least `BLOCKALIGN`.
- `iallocbp` allocates from a `Bpool` freelist or creates a new aligned block for that pool.
- `growbp` preallocates a batch of `Block` headers and backing storage for a `Bpool`.
- `checkb` validates block pointer fields and panics on poisoned or out-of-range buffers.

Notable dependencies:
- Kernel heap allocation, `Block`, `Bpool`, and block flags from shared port data.
- Interrupt locks for pool freelists.

Research notes:
- Blocks reserve 64 bytes of headroom and 16 bytes of trailer space by default.
- Pooled blocks are reset to `BINTR` on free and reuse, reflecting interrupt-safe network use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/allocb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/aoe.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/aoe.h

ATA over Ethernet protocol definitions shared by AoE code.

Key contents:
- AoE command enums for ATA, config, mask, and reserve/release operations.
- Config command values and mask/reservation directive and error codes.
- AoE EtherType, sector size, maximum config length, structure sizes, version, flags, and ATA flags.
- Wire-format structs:
  - `Aoehdr`: Ethernet + AoE header.
  - `Aoeata`: ATA command payload.
  - `Aoecfg`: config payload.
  - `Aoemd`: mask directive entry.
  - `Aoem`: mask command header.
  - `Aoerr`: error response with flexible Ethernet address list.
- External error strings `Echange` and `Enotup`.

Notable dependencies:
- `Eaddrlen` from network headers.

Research notes:
- Structures are byte-array wire formats rather than host-endian integer structs, which avoids alignment/endian assumptions in the header itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/aoe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/audioif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/audioif.h

Portable audio device interface definitions.

Key contents:
- `Audio` device object with device name, controller/mixer pointers, open refs, read/write/close callbacks, volume callbacks, control/status callbacks, buffered callback, delay/speed fields, controller number, and linked-list pointer.
- Volume channel/type enum values for left, right, stereo, and absolute, with `Mono` aliased to `Left`.
- `Volume` descriptor containing name, register, range, type, and capability bits.
- Prototypes for `addaudiocard`, `genaudiovolread`, and `genaudiovolwrite`.

Notable dependencies:
- Kernel `Ref` and audio-device implementations that provide the callback functions.

Research notes:
- This is an interface header only; policy and device behavior live in individual audio drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/audioif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/auth.c

Portable authentication/user identity helpers and related system calls.

Key behavior:
- Defines global `eve` and `hostdomain`.
- `iseve` checks whether the current process user is the host owner.
- `sysfversion` validates a user version string and negotiates a 9P mount version on a file descriptor via `mntversion`.
- Deprecated `sys_fsession` validates and clears a user buffer for compatibility.
- `sysfauth` validates an auth name, obtains an auth channel through `mntauth`, and returns a close-on-exec fd.
- `userwrite` allows any user to become `none` through the console user device.
- `hostownerwrite` requires `eve`, validates the new owner name, renames users across process/server/share state, updates `eve`, and sets the current process user.
- `hostdomainwrite` requires `eve`, validates and stores the host domain.

Notable dependencies:
- Mount/auth channel operations, fd allocation, process user management, and auth server constants.

Research notes:
- `sysfauth` carefully transfers responsibility for the original channel to the auth channel after `mntauth`.
- Host owner changes propagate through multiple subsystems before replacing the global owner string.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/cache.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/cache.c

Portable client-side file data cache for mount channels.

Key behavior:
- `cinit` preallocates a fixed set of `Mntcache` entries and creates the `fscache` image used for cached pages.
- Caches are keyed by channel type/dev/qid, tracked in a hash table and an LRU list.
- `Mntcache` has a recursive qlock because mount read-ahead can call cache update paths while already holding the cache lock.
- `copen` attaches or allocates a cache entry for non-directory channels, reusing entries by exact qid or qid ignoring version.
- `cread` reads contiguous valid cached page ranges, then falls back to mount read-ahead for misses.
- Cached page ranges are tracked per page through a bitmap and packed offset/end metadata in `Page.va`.
- `cupdate` and `cwrite` update cached data after reads/writes; writes bump qid versions and avoid caching append writes.
- `ctrunc` invalidates cached data and read-ahead state after truncation.
- `cclunk` resets read-ahead state and clears the channel’s cache pointer.

Notable dependencies:
- VM page cache/image primitives: `newimage`, `newpage`, `cachepage`, `lookpage`, `putpage`, `kmap`.
- Mount read-ahead helpers from `devmnt.c`.

Research notes:
- Cacheable range is capped at `MAXCACHE` per file.
- If memory pressure is detected while inserting pages, the code invalidates the remaining range rather than forcing cache population.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/chan.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/chan.c

Core Plan 9 channel, path, mount, walk, and name-resolution implementation.

Key behavior:
- Provides refcount helpers, kernel string duplication/copy helpers, channel device reset/init/shutdown dispatch, and `Chan` allocation/freeing.
- `newpath`, `copypath`, `pathclose`, `fixdotdotname`, `uniquepath`, and `addelem` maintain channel path strings and undo `..` components.
- Channel close supports queued close work through a dedicated close process, allowing `ccloseq` to defer device close operations.
- `cunique` clones a channel if it is shared by reference.
- `eqchan` and `eqchantdqid` compare channels by type/dev/qid with optional version skipping.
- Mount handling includes `newmhead`, `putmhead`, `cmount`, `cunmount`, mount ordering, union mount handling, and mount cache invalidation.
- `findmount`, `domount`, and `undomount` translate between mounted channels and underlying channels during walk/name resolution.
- `ewalk` wraps device walk operations and preserves path state.
- `walk` resolves a list of path elements with mount traversal and optional no-mount behavior.
- `namec` is the central name resolver for open, create, remove, access, and stat-style operations; it parses names, handles roots and device names, walks components, enforces permissions, performs create/open/remove/truncation behavior, and returns a prepared channel.
- Name validation helpers reject empty, overlong, or invalid names using the `isfrog` character table.
- `isdir` enforces directory channels and `dirchanstat` stats directory channels.

Notable dependencies:
- Device table operations, mount heads, process namespace state, path and channel structures from `portdat.h`.
- Error handling, permission checks, and cache invalidation hooks.

Research notes:
- This is one of the central VFS files: small semantic changes can affect all file namespace operations.
- Locking spans channel refs, mount table state, path refs, and deferred close queues; error unwinding is pervasive.
- `namec` is the highest-risk function due to its many modes and interactions with mount points, creates, removes, and open flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/cis.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/cis.c

PCMCIA Card Information Structure parser.

Key behavior:
- `pcmcistuple` searches attribute space first, then common memory, for a tuple/subtuple and copies tuple payload bytes.
- `pcmcisread` resets a `PCMslot`’s parsed config state and walks CIS tuples from attribute memory.
- Tuple handlers parse long-link multi-function tuples, version strings, config register bases/masks, and config table entries.
- Utility parsers decode little-endian variable-size integers, voltage/current encodings, timing encodings, I/O ranges, IRQ masks, and memory windows.
- Config entries populate `PCMconftab` fields such as index, default config, memory wait, Vpp, timing, I/O windows, 16-bit I/O capability, IRQ type/mask, and config-present state.
- Version tuples are normalized into semicolon-separated strings.

Notable dependencies:
- PCMCIA mapping functions `pcmmap` and `pcmunmap`.
- `PCMslot`, `PCMmap`, and `PCMconftab` architecture structures.

Research notes:
- The tuple scan has hard iteration limits for direct tuple lookup and stops on `0xff` end markers.
- IRQ masks are filtered with a hardcoded available-level mask.
- Memory-space tuple details are consumed to keep parsing in sync but not stored by this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/cis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dev.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/dev.c

Generic helper functions for Plan 9 kernel device implementations.

Key behavior:
- `mkqid`, `devno`, and `devdir` build qids and directory metadata.
- Extensive comments document the subtle expectations and contradictions around `Devgen`, `devwalk`, `devstat`, and `devdirread`.
- `devgen` implements table-backed directory generation, with the first table entry representing the directory itself.
- Default `devreset`, `devinit`, and `devshutdown` are no-ops.
- `devattach` creates a root channel for a device spec and constructs its path.
- `devclone` clones unopened channels.
- `devwalk` implements generic walking through a `Devgen`, including cloned-channel ownership and partial-walk behavior.
- `devstat` stats a channel through a generator, fabricating directory stats when needed.
- `devdirread` serializes directory entries from a generator into user buffers.
- `devpermcheck` checks permissions against file owner, `eve`, or other users.
- `devopen` performs generator lookup, permission checks, directory open restrictions, and marks the channel open.
- Default create/remove/wstat/power/config operations reject with `Eperm`.
- `devbread` and `devbwrite` adapt byte-oriented device read/write methods to `Block` I/O.

Notable dependencies:
- Device table, `Chan`, `Dirtab`, `Dir`, `Walkqid`, and Plan 9 directory serialization.
- Global `eve` and current process user.

Research notes:
- The comment block is important API documentation for writing correct device generators.
- `devdirread` treats too-small directory entry serialization as `Eshort` only when no entries have yet been copied.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dev.c -->