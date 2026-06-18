# Group Research: group_194_9front_sources_os_plan9_9front_sys_src_cmd_vl_asm_c_sources_os_plan9_297090c2f30f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/asm.c

This is the MIPS linker backend emitter for `vl`. It writes executable text/data, Plan 9 symbol and line tables, target headers, and final MIPS instruction encodings.

Key behavior:
- Provides endian-aware output macros and `objput`/`objhput`/`lput`, switching target long/halfword byte order through the global `little`.
- `asmb` emits text instructions, string constants, data blocks, optional symbols/line tables, then rewinds to write one of several supported executable headers: Unix ECOFF-like, Plan 9, SGI COFF, ELF, or headerless.
- `asmsym` and `putsymb` emit Plan 9 symbol records for text, leaf text, data, bss, string constants, file history, frames, autos, and params.
- `asmlc` emits compressed line-number deltas.
- `datblk` materializes initialized data/string bytes, detects duplicate initialization, and handles integer, string, and floating constants with host/target byte-order maps.
- `asmout` maps `Optab.type` templates to concrete MIPS words, including synthetic multiword sequences for large constants, long memory references, FP loads/stores, case tables, jump delay-slot folding, LL/SC, HI/LO, CP0, and FP control registers.
- `oprrr`, `opirr`, and `vshift` encode the instruction format constants used by `asmout`.

Integration and risks:
- Relies on `span.c`/`optab.c` to classify operands and choose instruction templates before emission.
- Header generation is strongly tied to `HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, and `entryvalue`.
- Several paths assume fixed MIPS instruction widths and Plan 9 symbol encoding; changing `Optab.type` values requires matching `asmout`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/compat.c

This file only includes `l.h` and the shared C compiler compatibility implementation from `../cc/compat`.

Key behavior:
- Pulls the linker’s compatibility helpers into the `vl` build rather than defining local logic.

Integration and risks:
- Behavior is entirely inherited from `../cc/compat`; changes there affect this linker.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/l.h

This is the central private header for the MIPS linker `vl`.

Key contents:
- Defines linker IR structs: `Adr`, `Prog`, `Sym`, `Auto`, `Optab`, `Oprang`, `Count`, and opcode cross-reference storage.
- Defines symbol classes (`STEXT`, `SDATA`, `SBSS`, etc.), operand classes (`C_REG`, `C_SCON`, `C_LBRA`, etc.), scheduler flags, buffer limits, hash sizes, and scheduling window constants.
- Declares global linker state for headers, entry/data/text addresses, object buffers, symbol tables, current text/function state, line/symbol sizes, library lists, endian maps, and delay-slot statistics.
- Declares formatting, loading, patching, data layout, scheduling, span, assembly, symbol, and utility functions.

Integration and risks:
- Shared across all `vl` implementation files, so struct layout and enum values are ABI-like within the linker.
- `Adr` and `Prog` cache operand classes and optab indices; code that mutates operands must call `nocache`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/list.c

This file implements diagnostic/listing formatters for linker instructions and operands.

Key behavior:
- `listinit` registers Plan 9 format verbs `%A`, `%D`, `%P`, `%S`, and `%N`.
- `Pconv` formats a `Prog` with line number, scheduling marker, opcode, operands, and optional register.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats registers, memory references, constants, branch targets, FP constants, and string constants.
- `Nconv` formats name spaces such as `SB`, `SP`, `FP`, extern/static/auto/param references.
- `Sconv` escapes string constants for listings.
- `diag` prefixes errors with the current text symbol, counts errors, and aborts after more than ten.

Integration and risks:
- `Dconv` depends on global `curp` for branch target formatting.
- These formatters are used heavily by debug flags and error paths; bad formatter assumptions can obscure linker diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/noop.c

This file rewrites pseudo-instructions, marks scheduling boundaries, inserts stack-frame prologues/epilogues, expands returns, and invokes local instruction scheduling.

Key behavior:
- `noops` finds leaf functions, frame sizes, BECOME requirements, labels, sync points, branch targets, and strips `ANOP`.
- Expands `ATEXT` into stack adjustment and link-register save when needed.
- Expands ordinary `ARET` into restore/stack-adjust/jump sequences, with special handling for leaf functions.
- Expands BECOME-style returns from `RET $n`.
- Marks hard scheduling barriers for control transfer, system/TLB/case operations, special CP0/FP control moves, and cache-sensitive sequences.
- Splits instruction stream into schedulable blocks and calls `sched`.
- `addnop` inserts canonical MIPS NOP (`NOR R0,R0,R0`); `nocache` clears cached optab/class fields.

Integration and risks:
- Depends on `curtext`, `autosize`, and `Sym.frame/become` metadata later consumed by codegen.
- Must preserve delay-slot and scheduling correctness around branches, returns, and special registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/obj.c

This is the main program and Plan 9 object/archive loader for the MIPS linker.

Key behavior:
- `main` parses linker flags, selects output header defaults, initializes global state, opens output, loads object files/libraries, then runs `patch`, optional profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, and `undef`.
- `objfile` opens regular objects or Plan 9 archives and lazily loads archive members that satisfy unresolved `SXREF` symbols.
- `ldobj` decodes Plan 9 object records, symbol names, addresses, histories, globals, dynamic/init/data records, text records, branch offsets, and floating constants.
- Supports autolib path construction from history records with `$O`/`$M` expansion.
- Maintains file-history autos, local static symbol versions, duplicate-text skipping with `DUPOK`, and data records linked through `datap`.
- `doprof1` and `doprof2` inject profiling/tracing instrumentation.
- `nuxiinit`, `ieeedtof`, and `ieeedtod` provide byte-order maps and floating conversion.

Integration and risks:
- Object decoding assumes the Plan 9 compiler object format and fixed maximum record sizes.
- Archive loading loops until unresolved symbols stop being resolved; incorrect `SXREF` state can affect library inclusion.
- Profiling insertion mutates instruction streams before scheduling/span.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/optab.c

This file defines the MIPS instruction selection table used by the linker backend.

Key behavior:
- `optab` maps opcode plus operand classes to an `Optab.type`, emitted byte size, and default base register parameter.
- Covers text pseudo-ops, register moves, integer ALU ops, shifts, loads/stores, large constants, branches/jumps, FP ops, FP memory access, CP0/FP control moves, cache/break, case tables, and LL/SC.
- Several entries share generic forms; aliases are established later by `buildop` in `span.c`.
- The comment notes some operations are unfinished, especially some 64-bit/double memory and arithmetic combinations.

Integration and risks:
- `Optab.type` numbers are interpreted directly by `asmout`; table changes must stay synchronized.
- The table is sorted in-place by `buildop`, so code should not assume source order after initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/pass.c

This file performs data layout, control-flow following, branch patching, and small numeric utilities.

Key behavior:
- `dodata` validates data initializers, optionally marks string constants, lays out small data first, then larger data, then bss, and creates literal-pool data for large constants/symbol addresses.
- Defines linker symbols such as `setR30`, `bdata`, `edata`, `end`, and `etext`.
- `undef` reports unresolved external symbols.
- `follow` rebuilds the program order from text symbols through `xfol`, reducing jumps and arranging fall-throughs.
- `xfol` follows unconditional jumps, copies short instruction sequences when useful, inverts conditional branches when needed, and preserves `NOSCHED` regions.
- `patch` resolves symbolic branch/jump/return targets, builds forward skip links, and collapses chains of jumps through `brloop`.
- Includes `atolwhex` and `rnd`.

Integration and risks:
- Literal pooling rewrites instruction operands and must clear optab caches.
- Branch following and copying are sensitive to labels, `FOLL`, `NOSCHED`, and delay-slot expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/sched.c

This file implements local instruction scheduling for MIPS delay slots and load/use hazards.

Key behavior:
- Builds `Sch` side records for up to `NSCHED` instructions with integer, floating, condition/special-register, and memory dependency sets.
- `regsused` classifies source/destination operands, load markers, branch/fcmp markers, memory offsets/sizes, HI/LO, CP0, FP control, and atomic LL/SC constraints.
- `sched` performs a prepass to group non-conflicting loads and find filler instructions, then tries to fill load/branch/fcmp delay slots or inserts NOPs.
- Tracks delay-slot statistics for load, branch, fcmp, and HI/LO hazards.
- `depend`, `conflict`, and `offoverlap` enforce scheduling safety, including same-address device-load ordering and atomic instruction barriers.
- `compound` treats multiword emissions and writes to `REGSB` as nontrivial for scheduling.

Integration and risks:
- Depends on accurate operand classes from `aclass` and instruction sizes from `oplook`.
- Conservative memory dependency rules are important for MMIO-like loads and stack/global aliasing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vl/span.c

This file assigns instruction PCs, resolves text size, classifies operands, and builds opcode lookup accelerators.

Key behavior:
- `span` walks the instruction stream assigning PCs, using `oplook` sizes, updating text symbol values, and adding workarounds for early MIPS 4000 page-boundary delay-slot bugs via `pagebug`.
- Repeats layout when large procedures require short branches to be expanded into branch-around-jump sequences.
- Optionally places string constants in text for debug mode.
- Computes `textsize`, `INITDAT`, and `etext`.
- `aclass` maps `Adr` operands into linker classes and computes `instoffset` for constants, extern/static/auto/param references, branches, and memory references.
- `oplook` selects and caches `Optab` entries, using exact ranges or precomputed `opcross` tables.
- `cmp`, `buildop`, and `buildrep` establish class compatibility, sorted opcode ranges, aliases, and fast replicated lookup tables.

Integration and risks:
- `pagebug` mutates branch-like instructions into NOP-plus-copy sequences before final layout.
- Operand classification reports undefined externals and may force symbols to `SDATA` to continue.
- `buildop` depends on fixed class enum assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vl/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/9p.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/9p.c

This file exposes a minimal 9P debug/control filesystem for a running VM.

Key behavior:
- Creates `mem`, `regs`, `kregs`, and `xregs` files under a posted 9P service.
- `mem` reads/writes guest virtual memory through `vmemread` and `vmemwrite`.
- `regs`/`kregs` synthesize a Plan 9 `Ureg`-style binary register image by reading textual registers from `regsfd` and using `libmach` register layouts for i386/amd64.
- `xregs` proxies raw register reads directly from `regsfd`.
- Offsets are normalized through `off2addr` to preserve signed address behavior.

Integration and risks:
- Depends on host pointer width to choose `mi386` vs `mamd64`.
- Register parsing assumes `/dev/vmx`-style textual register names match `libmach`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/dat.h

This is the shared VMX data-model header for memory regions, PCI devices, VGA modes, interrupts, and x86 access helpers.

Key contents:
- Defines VM states, register-name macros, page size, MMIO operation constants, and IRQ special values.
- `Region` describes guest physical mappings, permissions, optional segment backing, BIOS/E820 type, and MMIO callbacks.
- `PCIDev`, `PCIBar`, and `PCICap` model simple PCI config space, BARs, caps, and IRQ state.
- `VgaMode` describes framebuffer modes.
- `TLB` caches recent guest x86 memory translation/access state.
- Declares shared globals such as `mmap`, `state`, `debug`, `irqactive`, `cmos`, and `kconfig`.

Integration and risks:
- Many implementation files share these structs directly, so layout changes ripple widely.
- E820 region type is encoded in the high bits of `Region.type`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/exith.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/exith.c

This file handles VM exits and selected trapped x86 instructions/events.

Key behavior:
- Parses exit messages into `ExitInfo`, updates reported PC/SP/AX metadata, and dispatches by exit name.
- Handles port I/O exits, including string I/O with segment/address-size handling and `x86access`.
- Handles EPT faults by attempting single-step emulation through `x86step`.
- Initializes and filters CPUID leaves, exposes a KVM-like hypervisor leaf, masks unsupported features, and sizes XSAVE state based on `xcr0`.
- Handles RDMSR/WRMSR for PAT, microcode update, and `IA32_MISC_ENABLE`; unknown MSRs are debug-logged.
- Handles debug/control-register moves, debug exceptions, HLT, IRQ ack notifications, and XSETBV validation.
- Unknown instruction exits inject `#ud`; unknown fatal exits either mark VM dead or call `sysfatal` depending on `persist`.

Integration and risks:
- CPUID masking is a guest compatibility contract; changing it can break OS boot.
- String I/O must correctly update RCX/RSI/RDI on partial fault.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/exith.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/fns.h

This is the shared function/macro declaration header for VMX.

Key contents:
- Declares allocation, kernel loading, register get/set, VM exit handling, timers, VM errors/debug, control operations, MMIO, IRQ, exceptions, VGA, UART, notifications, PCI, guest memory mapping, disk/net device creation, x86 access/step, and I/O helpers.
- Defines `MIN`, `MAX`, `vmdebug`, and unaligned-looking `GET*`/`PUT*` memory access macros.

Integration and risks:
- The `GET*`/`PUT*` macros cast directly to integer pointers, assuming the host tolerates these accesses and using host endian layout.
- Function prototypes connect nearly every VMX device file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/ide.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/ide.c

This file implements an emulated legacy IDE/ATA PIO disk controller.

Key behavior:
- Models up to four IDE devices with ATA status/error/control/taskfile registers and per-drive asynchronous I/O state.
- Supports reset, IRQ signaling on IRQ14/15, CHS and LBA sector addressing, address incrementing, PIO read/write buffering, identify-device data, read verify, diagnostics, set translation mode, and selected set-feature commands.
- Uses a background `ideioproc` per disk to read from the backing file and to record writes in an in-memory sector overlay.
- `ideio` handles primary/secondary command/data/control port reads and writes, including 16/32-bit data port transfers.
- `mkideblk` opens a disk image, computes geometry, updates CMOS/int13 metadata, initializes the drive, and starts the I/O process.

Integration and risks:
- Writes are not persisted to the backing file; they are stored in an in-memory sector list.
- Identify-device construction uses fixed strings/fields and has a couple of suspicious `PUT16(d, ...)`/`PUT32(d, ...)` writes where `p` appears intended.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/ide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/io.c

This file implements most legacy PC I/O-port devices and central I/O dispatch.

Key behavior:
- Emulates CMOS/RTC, including memory-size initialization, BCD time fields, periodic interrupt timing, and IRQ8 updates.
- Emulates dual 8259 PICs, IRQ lines, acknowledge, ELCR edge/level mode, ICW/OCW programming, priority, mask, poll, and automatic EOI.
- Emulates PIT channels and port 0x61 speaker latch enough for timers and IRQ0.
- Emulates i8042 keyboard/mouse controller, keyboard command ACKs, PS/2 mouse modes, packet generation, IntelliMouse detection sequence, IRQ1/IRQ12, and reset pulses.
- Emulates two UARTs with optional file-backed input/output processes and IRQ generation.
- Provides a dummy floppy controller and several no-op legacy port ranges used by probes/delays.
- `handlers` maps fixed port ranges; `io0` falls through to PCI I/O BARs; `io` masks transfer sizes and optional per-port debug logging.

Integration and risks:
- Device emulation is intentionally partial but tuned for guest OS boot/probing.
- Timer and interrupt behavior depends on `nanosec`, `settimer`, and VM state transitions.
- Keyboard/mouse channels are shared with `vga.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/ksetup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/ksetup.c

This file loads guest kernels and prepares boot protocol data for Multiboot, OpenBSD ELF, and Linux boot-protocol kernels.

Key behavior:
- Provides packing helpers for mixed 32/64-bit boot structures, BIOS memory-map export, command-line construction, and boot module loading.
- `trymultiboot` validates a Multiboot header, loads the kernel image, builds a multiboot info block with memory map, cmdline, modules, and framebuffer info, then seeds EAX/EBX/PC.
- ELF support parses 32/64-bit little-endian ELF headers, program headers, section headers, symbols, string tables, and loadable segments, rejecting dynamic/interpreter images.
- OpenBSD support detects `ostype` or ramdisk symbols, preserves selected debug/symbol sections, builds bootarg chains for memory map, console, DDB, EFI framebuffer, and parses OpenBSD-specific command-line settings.
- Linux support validates boot protocol >= 2.06, loads bzImage payload, builds zero page, cmdline, optional initrd, screen info, GDT, E820 map, and register state.
- `loadkernel` tries Multiboot, ELF/OpenBSD, then Linux.

Integration and risks:
- Strongly tied to guest memory availability through `gptr`, `gpa`, `gavail`, and `mmap`.
- OpenBSD/Linux boot structs are hand-packed at fixed offsets; protocol drift can break newer kernels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/ksetup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/nanosec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/nanosec.c

This file provides a monotonic-ish nanosecond timer for VM device emulation.

Key behavior:
- Prefers `cycles()` scaled by `_tos->cyclefreq` so time is not adjusted by wall-clock synchronization.
- Falls back to `nsec()` if cycle frequency is unavailable.
- Returns elapsed nanoseconds relative to first initialization.

Integration and risks:
- First call initializes state and returns zero.
- Timer users assume monotonic behavior for PIT/RTC/input watchdog scheduling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/nanosec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/pci.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/pci.c

This file implements a simple PCI bus/config-space model.

Key behavior:
- Creates PCI devices, assigns incrementing BDFs, creates BARs and capabilities, and initializes a host bridge.
- Maintains linked lists of active memory and I/O BARs according to command register enable bits.
- Handles config address/data ports 0xcf8/0xcfc, including partial-byte masks.
- Exposes standard config fields: vendor/device, command/status, class/rev, BARs, subsystem ID, capability pointer, and interrupt line/pin.
- Tracks PCI IRQ activity and maps active device IRQs to PIC lines.
- `pcibusmap` auto-assigns I/O BAR addresses, rotates through a small IRQ set, sets ELCR level mode, and initially deasserts assigned IRQ lines.

Integration and risks:
- Memory BARs are mostly unsupported for bus mapping except for explicit users such as VGA.
- BAR sizing/rounding is minimal but adequate for vmx’s own virtio/VGA devices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vesa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vesa.c

This file implements VESA BIOS/VBE services through a small guest ROM and port-mediated helper thread.

Key behavior:
- Installs a synthetic option ROM at 0xc0000, BIOS vector pointer, OEM strings, and a mode table.
- Uses ports 0xfee0-0xfeef as a protocol between real-mode guest BIOS code and the `vesathread`.
- Handles VBE functions for controller info, mode info, set/get mode, logical scanline length, DAC palette format, palette data, and DDC/EDID.
- Synthesizes VBE mode descriptors and EDID timing blocks from configured `VgaMode` entries.
- Manages palette updates through `vgasetpal`/`vgagetpal`.
- `vesainit` appends standard legacy VESA modes and starts the helper thread.

Integration and risks:
- Depends on `vga.c` globals for modes, framebuffer address/size, and display state.
- Real-mode BIOS interface is custom and partial; unsupported VBE functions return failure and log debug messages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vesa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vga.c

This file implements VGA/VESA display state, framebuffer rendering, keyboard layout/input capture, and mouse capture.

Key behavior:
- Emulates basic VGA ports for attribute, sequencer, graphics, CRTC, misc output, and palette registers.
- Maintains text mode memory at 0xb8000, framebuffer memory at configured guest physical address, and 256-color palette images.
- Renders text mode using CP437 mapping and Plan 9 draw fonts, including blinking cursor.
- Renders framebuffer modes with dirty-line tracking, colormap expansion for VESA 4/8-bit modes, and direct/scratch image upload paths.
- Parses framebuffer specs such as `text`, raw modes, or `vesa:` mode lists with optional framebuffer address.
- Loads `/dev/kbmap`, maps Plan 9 keyboard runes to PC scan codes, watches `/dev/kbd`, and emits scan-code make/break bytes to the i8042 channel.
- Captures/re-centers mouse input, supports release chord, and forwards relative movement/buttons to PS/2 mouse emulation.
- `vgainit` initializes draw/mouse/keyboard/draw processes and, for VESA, creates a PCI VGA-like device plus framebuffer BAR.

Integration and risks:
- Shares `kbdch`, `mousech`, and `mouseactive` with `io.c`.
- Direct framebuffer writes are polled by `drawproc`; display refresh interval is fixed at roughly 20 ms.
- VESA mode parsing enforces channel compatibility and framebuffer sizing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/virtio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/virtio.c

This file implements legacy PCI virtio queue handling plus virtio-net and virtio-block devices.

Key behavior:
- Defines shared virtio device, queue, and descriptor-chain structures.
- `viogetbuf` waits for DRIVER_OK, validates descriptor chains, maps guest buffers with `gptr`, and tracks live buffers.
- `vioputbuf` writes used-ring entries, wakes reset waiters, and raises PCI interrupts unless suppressed.
- `vioqread`, `vioqwrite`, and `vioqrem` move bytes across readable/writable descriptor segments.
- Implements legacy I/O-port virtio registers for features, queue select/address/size/notify, device status, and ISR status.
- `mkvionet` creates a virtio-net PCI device with RX, TX, and control queues, optional MAC address, file or dialed network backend, feature bits, and RX/TX worker processes.
- Virtio-net supports MAC filtering, multicast/unicast bloom filters, promiscuous/allmulti/alluni/nobcast flags, MAC-table and MAC-address control commands, optional 10-byte host-side packet header, minimum Ethernet padding, and interrupt delivery.
- `mkvioblk` creates a virtio-block PCI device backed by a file, with one queue and a worker supporting read/write sector requests.

Integration and risks:
- Queue reset waits for outstanding live buffers; invalid queue addresses are tolerated but logged.
- Virtio-block computes bounds in bytes from 512-byte sectors and uses simple synchronous file I/O.
- Network backend setup can use Plan 9 `dial` with control operations or a raw file descriptor.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/virtio.c -->