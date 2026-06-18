# Group Research: group_27_9front_sources_os_plan9_9front_sys_src_9_teg2_l_s_sources_os_plan9_9f_53c3c3947fba

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/l.s

Tegra 2 ARMv7 bootstrap and low-level machine support.

Purpose:
- Starts CPU0 from U-Boot or another Plan 9 kernel with the MMU off.
- Parks secondary CPUs until `cpus_proceed`, then starts them through `cpureset`.
- Builds early L1 section mappings for DRAM and MMIO, enables caches/MMU, warps execution into `KZERO`, then calls `main`.

Key behavior:
- Contains early serial progress output, memory diagnostic probing, Mach setup, physical/virtual address conversion, and `setmach`.
- Provides cache-line maintenance, TLB invalidation, CP15 register accessors, interrupt priority routines, `setlabel`/`gotolabel`, `wfi`, `coherence`, `cas`, and `_tas`.
- Includes `cache.v7.s` for broader cache operations.

Integration:
- Supplies primitives used by `main.c`, `mmu.c`, `trap.c`, and locking code.
- Depends on constants and macros from `arm.s`/`mem.h`.

Risks/notes:
- Locking atomics depend on L1 cache/exclusive monitor state.
- Early mappings and cache/TLB order are hardware-sensitive; comments show empirical sequencing for Tegra 2/Cortex-A9.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/lexception.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/lexception.s

ARM exception-vector entry code for Tegra 2.

Purpose:
- Defines `vectors` and `vtable`, which `trapinit()` copies to low and high vector pages.
- Handles reset, SWI/syscall, undefined instruction, prefetch abort, data abort, IRQ, FIQ, and hypervisor-call vector entries.

Key behavior:
- `_vsvc` saves user registers into a `Ureg`, restores kernel `SB`, recovers `m`/`up`, calls `syscall`, then returns through `rfue`.
- `_vswitch` normalizes abort/IRQ/undefined entries into SVC-mode `trap(Ureg*)` calls for both user and kernel exceptions.
- `setr13` installs banked stack/save-area pointers for ARM exception modes.

Integration:
- Pairs directly with `trap.c` trap decoding and `lproc.s` user return.
- Uses `machaddr`, `MACH`, `USER`, and Plan 9 ARM calling conventions.

Risks/notes:
- Stack layout is exact and shared with `Ureg` consumers.
- FIQ and hypervisor-call vectors are mostly diagnostic stubs that print markers and return.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/lproc.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/lproc.s

Small ARM process-transition assembly.

Purpose:
- Implements the first jump from kernel to user mode and fork return.

Key behavior:
- `touser` installs the user stack pointer into banked user SP, builds a user-mode return frame, and returns to `UTZERO+0x20` with `RFEV7W`.
- `forkret` adjusts from saved process trap frame layout and branches to `rfue` to resume the child process.

Integration:
- Called by `init0()` in `main.c` and by scheduler/fork setup in common kernel code.
- Shares `Ureg` stack-frame conventions with `lexception.s` and `trap.c`.

Risks/notes:
- Extremely layout-sensitive; any `Ureg` or stack convention change must be reflected here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/main.c

Tegra 2 kernel bootstrap, configuration, memory sizing, and reboot path.

Purpose:
- Orchestrates CPU0 initialization after `l.s` reaches C.
- Parses early `plan9.ini` data from `CONFADDR`.
- Initializes caches, MMU, traps, memory pools, devices, PCI, processes, and secondary CPUs.

Key behavior:
- `plan9iniinit`, `getconf`, `addconf`, and `writeconf` manage boot configuration.
- `mach0init`, `machinit`, `launchinit`, `machon`, and `machoff` manage per-CPU `Mach` state.
- `main` performs ordered boot: BSS clear, SMP/cache setup, console, MMU, config, trap, memory, devices, page allocator, user process, secondary CPU startup, scheduler.
- `confinit` probes memory, computes page/process/image/swap sizing, and sets copy-on-reference mode.
- `reboot` shuts down devices, copies `rebootcode` to `REBOOTADDR`, disables caches through the trampoline, and jumps to the next kernel.

Filesystem relevance:
- Initializes channel devices, page allocator, process environment, and storage-visible PCI/device layers before filesystems/userspace can run.

Risks/notes:
- Boot order is fragile: traps must exist before memory probing; locks need SMP/cache setup; malloc availability is called out explicitly.
- Memory sizing assumes 1 GiB DRAM and reserved high-memory regions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/mem.h

Tegra 2 memory layout and MMU constants.

Purpose:
- Defines machine-wide sizes, alignment, kernel/user address layout, page constants, PTE flags, and physical/virtual MMIO regions.

Key definitions:
- 4 KiB pages, 32-byte cache lines, 4 CPUs max, 16 KiB kernel stacks, 1 GiB DRAM target.
- `KZERO`/`KSEG0` at `0xC0000000`, `KTZERO` at `KZERO+0x410000`, user space below roughly 1 GiB.
- Reserves high memory for vectors and L2 page tables through `RESRVDHIMEM`.
- Defines Tegra-specific regions for CPU MMIO, PL310 L2, exception vector peripheral, console UART, AHB, and NOR mappings.

Integration:
- Used by C and assembly, especially `l.s`, `mmu.c`, `trap.c`, and device drivers.

Risks/notes:
- Constants encode board-specific assumptions; changing DRAM size, vectors, or MMIO windows affects boot mappings and allocator boundaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/mmu.c

ARMv7 MMU setup and per-process mapping for Tegra 2.

Purpose:
- Builds kernel mappings, device mappings, high-vector mappings, and per-process user page tables.
- Provides runtime mapping helpers used by VM and device code.

Key behavior:
- `mmuinit` maps IO/NOR/AHB regions, creates high-vector L2 mapping, makes kernel text read-only, and clears user L1 space.
- `expand` converts 1 MiB ARM section mappings into coarse L2 tables when fine-grained page mappings are needed.
- `mmuswitch`, `flushmmu`, `mmurelease`, and `putmmu` maintain process user mappings via `Proc.mmul2`.
- `mmuuncache`, `mmukmap`, `mmukunmap`, `vmap`, and `vunmap` provide limited kernel/device mapping helpers.
- Uses explicit L1/L2 cache writeback and TLB invalidation around page-table changes.

Integration:
- Depends on `l.s` CP15/TLB/cache primitives and `main.c` `l2pages` reservation.
- Feeds Plan 9 VM fault handling through `putmmu`.

Risks/notes:
- Comments state L2 cache ops are empirically required for page tables.
- L2 page allocation wastes full pages for 1 KiB ARM coarse tables.
- `mmul1empty` contains disabled incremental-clearing code marked buggy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/pciteg.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/pciteg.c

Tegra 2 PCI/PCIe configuration-space access and scan setup.

Purpose:
- Provides Plan 9 PCI config read/write callbacks for Tegra 2/TrimSlice.
- Initializes PCI controller scanning and root device list.

Key behavior:
- Models Tegra PCI controller/port register layout and PCIe capabilities.
- `pcicfginit` verifies NVIDIA/Realtek presence, enables memory and bus-mastering, sets scanning limits, installs TBDF formatting, and scans bus 1 by default.
- `tegracfgaddr` maps TBDF/register offsets into Tegra config or extended config windows.
- `pcicfgrw8/16/32` implement config access; 32-bit reads probe the address first to avoid faults.
- `pcieintrdone` clears a magic AFI interrupt status register.

Filesystem relevance:
- Enables PCI-attached devices such as network/storage controllers that may host boot or file service paths.

Risks/notes:
- Comments say scanning beyond known buses can hang.
- Contains a Realtek interrupt hack and multiple board-specific assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/pciteg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/rebootcode.s

ARMv7 low-memory reboot trampoline.

Purpose:
- Runs from `REBOOTADDR` after `main.c` copies it there.
- Disables caches/MMU and copies a new kernel image to its physical destination before jumping to the new entry point.

Key behavior:
- `main` prints reboot progress, calls `cachesoff`, warps to physical execution, copies kernel code with `memmove`, and branches to the physical entry address.
- `cachesoff` drains and disables L1 cache/MMU/control bits with barriers.
- Includes local `_r15warp`, `panic` stub, `pczeroseg` stub, and `printhex`.

Integration:
- The C `reboot()` function prepares arguments and cache state, then jumps here.

Risks/notes:
- Must fit below page-table-sensitive low-memory limits.
- Assumes PL310/L2 is already off before entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/trap.c

ARM GIC v1 setup, IRQ dispatch, exception handling, and diagnostics.

Purpose:
- Initializes exception vectors and Tegra ARM interrupt controller state.
- Dispatches IRQ handlers, handles data/prefetch faults, undefined instructions, syscall aftermath, and kernel/user notifications.

Key behavior:
- Defines GIC distributor and CPU interface register layouts.
- `trapinit` copies vector code to high and low vector pages, sets exception-mode stack save areas, verifies ARM GIC IDs, configures priorities/targets, and enables distributor/CPU interface.
- `irqenable` and `irqdisable` manage `Vctl` chains and mask/unmask interrupts.
- `irq` acknowledges, dispatches, dismisses, masks unexpected IRQs, and records service-time histograms.
- `datafault` decodes ARM fault status and routes translation/permission faults to VM `fault`.
- `probeaddr` uses a `m->probing` flag to turn selected kernel data aborts into `-1`.

Integration:
- Works with `lexception.s` frame construction and `mmu.c` mappings.
- Exposes IRQ APIs used by UART, PCI, timer, and other device drivers.

Risks/notes:
- Uses direct MMIO register writes instead of bulk memory ops because comments report distributor-register aborts.
- `irqtooearly` blocks premature IRQ registration until kernel memory/device init is ready.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/uarti8250.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/uarti8250.c

Tegra console UART driver using an 8250-like register model.

Purpose:
- Provides `PhysUart i8250physuart` and sets `consuart` for early and normal console I/O.

Key behavior:
- Defines UART register offsets and bit masks for line control, FIFO, modem, interrupt, and line status.
- Implements status reporting, FIFO setup, DTR/RTS, modem control, parity/stop/bits configuration, break, interrupt-driven transmit/receive, enable/disable, and polled getc/putc.
- Uses sticky shadow registers for write-only or stateful registers.
- `uartconsinit` binds the single configured UART at `PHYSCONS`.

Integration:
- Used early by `main.c`/`l.s` boot diagnostics and later by Plan 9 UART/console layers.
- IRQ registration goes through `irqenable` from `trap.c`.

Risks/notes:
- Baud-rate programming is disabled under `notdef`; speed is effectively not changed.
- FIFO changes can lose receive data, so code waits for transmitter empty before toggling FIFO state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/v7-arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/v7-arch.c

Small ARMv7 utility routines.

Purpose:
- Provides cheap integer helpers outside cache assembly.

Key behavior:
- `ispow2` tests whether a `uvlong` is a power of two.
- `log2` returns the exponent of the smallest power of two greater than or equal to an input `ulong`, using `clz`.

Integration:
- Depends on ARM `clz` from `l.s`.
- Used by architecture/cache sizing code.

Risks/notes:
- `log2(0)` returns one greater than the computed CLZ-derived base, as intended by its “ceil log2” contract but worth preserving if reused.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/v7-arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/archxen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/archxen.c

Xen PC architecture adapter.

Purpose:
- Registers `PCArch archxen` with Xen-specific reset, interrupt, clock, and timer hooks.

Key behavior:
- `identify` disables PGE capability tracking.
- `intrinit` inspects xenstore CPU availability and honors `*nomp`/`*ncpu`, but ultimately limits the guest to one CPU with an SMP-not-supported message.
- `shutdown` calls `HYPERVISOR_shutdown(1)`.
- Provides placeholder I/O port, CR4, and MTRR functions needed by shared x86 code.

Integration:
- Referenced during Xen `main()` architecture initialization.
- Bridges generic Plan 9 PC kernel paths to Xen hypervisor routines.

Risks/notes:
- SMP discovery exists but SMP startup is explicitly not supported.
- Hardware I/O functions are stubs, suitable only for paravirtualized Xen assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/archxen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/cppx -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/cppx

`rc`/`awk` wrapper around C preprocessing for Xen headers.

Purpose:
- Preserves selected preprocessor lines while running `cpp -P`.

Key behavior:
- Skips `#include` lines.
- Quotes `#define`, continued macro, `#error`, and `#undef` lines with a temporary quote replacement.
- Pipes through `cpp -P`, then uses `sed` to restore literal quotes and unquote preserved directive text.

Integration:
- Supports generation/import of Xen public header data into Plan 9-compatible forms.

Risks/notes:
- Uses `£` as a temporary quote sentinel, which assumes that character will not occur meaningfully in input.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/cppx -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/dat.h

Xen-specific kernel data compatibility header.

Purpose:
- Extends the PC kernel data definitions with Xen ABI types, globals, and mapping helpers.

Key content:
- Includes `../pc/dat.h`.
- Defines fixed-width integer aliases and Plan 9-local errno constants expected by imported Xen headers.
- Includes `xendat.h` and normalizes `mk_unsigned_long` and guest-handle macros.
- Declares `hypervisor_virt_start`, `patomfn`, `matopfn`, `xenstart`, `xentop`, and `HYPERVISOR_shared_info`.
- Replaces normal `kmap`/`kunmap` with simple direct `KZERO`-based mappings.

Integration:
- Required by Xen MMU, console, storage, network, xenstore, and hypercall code.

Risks/notes:
- The “fake kmap” is explicitly questioned in comments and relies on Xen’s direct mapping model for this port.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/devrtc.c

Xen wall-clock RTC device.

Purpose:
- Provides Plan 9 `#r/rtc` device backed by Xen wall-clock time.

Key behavior:
- Directory contains `.` and `rtc`.
- `rtcread` returns `xenwallclock()` as a numeric value.
- `rtcwrite` accepts writes to `rtc` but ignores contents and returns byte count.
- Standard Plan 9 device methods delegate attach/walk/stat/open to common helpers.

Integration:
- Supplies time-of-day access in the Xen kernel without hardware CMOS/RTC access.

Risks/notes:
- Writes do not change Xen wall-clock time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/devxenstore.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/devxenstore.c

Xenstore device and kernel RPC helper.

Purpose:
- Implements Plan 9 `#x` device for Xenstore control and watch access.
- Provides kernel helpers for reading/writing xenstore nodes.

Key behavior:
- Maps Xenstore shared ring at `XENBUS` and uses Xen event channel from `start_info`.
- `xwrite` and `xread` move request/response bytes through Xenstore ring indices with wraparound handling.
- `xsrpc` serializes requests, assigns request IDs, matches out-of-order responses, handles watch events, and queues response payloads.
- Exposes `#x/xenstore` and `#x/xenwatch`.
- `xscmd`, `xenstore_read`, `xenstore_write`, `xenstore_setd`, and `xenstore_gets` provide in-kernel synchronous commands.
- `xenbusproc` watches `control/shutdown` and translates Xen poweroff/reboot requests into `reboot`/`exit`.

Integration:
- Required by Xen block/network frontend discovery, backend negotiation, console and shutdown handling.

Risks/notes:
- A comment flags a possible buffer overflow in `xscmd` when reading payloads into a fixed local buffer.
- Request matching logic is subtle because watch responses can arrive without a normal requester.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/devxenstore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/dpart.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/dpart.c

Boot-time disk partition discovery helper.

Purpose:
- Scans disks under `#S`, creates Plan 9 partition entries, then execs `/boot/boot2`.

Key behavior:
- Reads disk sectors with `readdisk` and writes partition definitions through each disk control file.
- Detects DOS/FAT and extended MBR partition types.
- `mbrpart` handles MBR, DMDDO offset, extended partition chains, Plan 9 partitions, and first DOS partition.
- `p9part` opens a Plan 9 partition and parses its textual partition table.
- `cdpart` detects El Torito boot floppy images and adds `cdboot`.
- `partall` binds console FDs, scans `#S/*/data`, and runs partition recognizers.

Filesystem relevance:
- Directly prepares block-device partition namespace before the second-stage boot program.

Risks/notes:
- A commented line says full `p9part(d, "data", 0)` scanning is “not safe yet”.
- Assumes sector sizes compatible with MBR parsing for `mbrpart`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/dpart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/etherxen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/etherxen.c

Xen virtual network interface frontend.

Purpose:
- Implements an `ether` driver named `xen` for Xen VIF devices.

Key behavior:
- Discovers VIFs through xenstore `device/vif/N`.
- Allocates shared TX/RX rings, grant references, event channel, TX frame pool, and RX frame pages.
- Publishes ring refs and event-channel to xenstore, requests rx-copy when backend supports it, and waits for backend `Connected`.
- `etherxenproc` drains outbound queue into TX grant frames.
- Interrupt handler processes RX and TX responses, recycles frames, re-posts RX buffers, and wakes transmit waiters.
- Supports control command `ea` to set Ethernet address and exposes interface stats.

Integration:
- Uses xenstore, grant-table helpers, event channels, Plan 9 `etherif`, and network block queues.

Risks/notes:
- Comments flag missing ID validation, checksum handling, and fixed speed reporting.
- `pnp` calls `intrenable` with `irq=-1` before attach also allocates a real event channel, which is notable and depends on Xen interrupt code tolerance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/etherxen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/fns.h

Function prototypes and macros for the Xen port.

Purpose:
- Extends shared Plan 9 port prototypes with x86 and Xen-specific declarations.

Key content:
- Declares architecture, CPU, FPU, MMU, trap, interrupt, timer, UART, and process-state functions.
- Defines `KADDR`, `PADDR`, no-op `dcflush`, Xen memory barriers, and `userureg`.
- Declares Xen console, MMU update/pinning, grant-table, event-channel, wall-clock, xenstore, and hypercall wrappers.
- Lists hypervisor calls used by this port: trap table, MMU update, event channel, console, grant table, memory op, shutdown, timer, callbacks, and more.

Integration:
- Central header for Xen C files and assembly cross-references.

Risks/notes:
- Several generic PC hooks remain declared even when Xen implementations are stubs or no-ops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/l.s

Xen x86 assembly bootstrap, low-level CPU helpers, hypercall glue, and vector stubs.

Purpose:
- Entry point from Xen’s Linux-style builder.
- Provides x86 low-level primitives for the Xen Plan 9 kernel.

Key behavior:
- `_start` records `xentop` and `xenstart`, clears flags, maps CPU0 Mach through `mmumapcpu0`, sets stack/SB, and enters C `main`.
- Defines common x86 helpers: CPUID/MSR/TSC, spl, atomic exchange, labels, halt/idle, FPU save/restore, string I/O stubs or routines as needed.
- Provides Xen-specific page-table update wrappers and hypercall dispatch helpers.
- Builds a dense `vectortable` of 256 six-byte vector entries, routing most vectors to stray handling and syscall vector to `_syscallintr`.

Integration:
- Works with `trap.c`, `plan9l.s`, `mmu.c`, and hypervisor ABI definitions.

Risks/notes:
- Vector-entry size is assumed by `trapinit`, which advances by 6 bytes per vector.
- Much code is inherited x86 kernel machinery adapted for Xen paravirtual constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/main.c

Main bootstrap and configuration for the Xen x86 Plan 9 kernel.

Purpose:
- Initializes the Plan 9 kernel as a Xen guest.

Key behavior:
- `options` parses Xen `start_info.cmd_line` as `plan9.ini`-style key/value lines.
- `main` initializes Mach state, Xen console, CPU, config, architecture, clock, allocator, traps, MMU, timers, FPU, keyboard/console, grant table, processes, devices, page allocator, first user process, and scheduler.
- `mach0init` and `machinit` set CPU0 Mach/PDB and map Xen shared info.
- `confinit` sizes usable memory below the hypervisor virtual window and sets process/image/swap/pool limits.
- Process hooks delegate to FPU helpers and flush TLB on save.
- `reboot` handles Xen shutdown for `entry == 0` or copies reboot trampoline for kernel restart.

Filesystem relevance:
- Initializes xenstore, virtual block/network devices, channel devices, page cache backing memory, and user boot environment.

Risks/notes:
- Memory above Xen’s mappable virtual boundary is ignored with a warning.
- Several boot comments reflect old PC assumptions adapted to Xen.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/mem.h

Xen x86 memory and address-space constants.

Purpose:
- Defines sizes, kernel/user virtual layout, Xen shared fixed mappings, segment selectors, and x86 PTE macros.

Key definitions:
- 4 KiB pages, 4 KiB kernel stack, up to 8 virtual CPUs.
- Kernel space starts at `KZERO=0x80000000`; user space is below that.
- Fixed Xen-related virtual addresses include `XENCONSOLE`, `XENSHARED`, `XENBUS`, and `XENGRANTTAB`.
- Segment selector aliases map to Xen-provided flat ring 1/ring 3 selectors.
- Defines PTE flags and index macros that switch between non-PAE and PAE behavior using `paemode`.

Integration:
- Used by Xen C and assembly for MMU, trap, console, and hypercall setup.

Risks/notes:
- PAE-aware macros rely on `paemode` global runtime state.
- Kernel/user split constrains usable memory mapping in `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/mmu.c

Xen paravirtual x86 MMU management.

Purpose:
- Maintains kernel and process page tables under Xen’s pinned page-table rules.
- Maps Xen machine frames and handles PAE/non-PAE switching.

Key behavior:
- `mmumapcpu0` detects PAE from Xen magic, initializes machine/physical mappings, and maps CPU0 Mach.
- `mmuinit` maps remaining guest memory and switches to the proper stack/page table context.
- `mmuflushtlb` switches page tables with Xen hypercalls or updates PDPT entries in PAE mode.
- `mmupdballoc`, `putmmu`, `mmuptefree`, `mmuswitch`, and `mmurelease` allocate, pin, update, unpin, recycle, and flush process page-directory/page-table pages.
- `mmuwalk` walks or creates kernel page-table entries for mappings.
- `mmumapframe` maps Xen machine frame numbers into fixed virtual slots.

Integration:
- Called by `main.c`, `devxenstore.c`, `uartxen.c`, grant/event-channel code, and VM fault paths.

Risks/notes:
- Comments document Xen refusing to pin pages still mapped writable by stale process tables; code loops around “bad” pages.
- SMP is not supported; several comments say PDB handling would need changes for multiprocessor guests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/plan9l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/plan9l.s

Plan 9 user-entry and syscall-vector assembly for Xen x86.

Purpose:
- Provides `touser` and direct syscall vector handling.

Key behavior:
- `touser` builds an x86 interrupt-return frame with user selectors, user stack, IF set, and entry `UTZERO+32`, loads user data segments, then `IRETL`s.
- `_syscallintr` saves segment and general registers, switches DS/ES to kernel data selector, calls `syscall(Ureg*)`, restores registers/segments, drops trap metadata, and returns with `IRETL`.

Integration:
- Used by `init0()` in `main.c` and by `trapinit` vector table from `l.s`.

Risks/notes:
- Assumes syscall vector `0x40` and exact `Ureg`/trap-frame stack layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/plan9l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/sdxen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/sdxen.c

Xen virtual block device frontend for Plan 9 `sd`.

Purpose:
- Implements `SDifc sdxenifc` for Xen VBDs.

Key behavior:
- Discovers likely Xen disk IDs from Linux major-device encodings.
- `xenverify` checks xenstore backend presence, allocates controller/ring/frame, event channel, and reads backend sector metadata.
- `backendconnect` publishes ring ref/event channel and waits for backend `Connected`.
- `xenonline` enables interrupts and marks frontend connected.
- `xenbio` serializes I/O, shares one page at a time, sends a single-segment block request, waits for interrupt completion, ends grant, and copies through an aligned bounce frame when needed.
- `sdxenintr` consumes block responses and wakes waiters.

Filesystem relevance:
- Provides the block device layer used by partitions and filesystems inside the Xen guest.

Risks/notes:
- Comments identify the implementation as simple and not performance-oriented.
- Single-page/single-request path limits throughput and relies on a bounce buffer for unaligned I/O.
- Ring overflow and richer `rio` paths are not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/sdxen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/trap.c

Xen x86 trap, syscall, page-fault, notification, and process-register handling.

Purpose:
- Installs Xen trap table entries and handles x86 exceptions in a paravirtual guest.

Key behavior:
- `trapinit` registers callbacks, installs all 256 vector entries with `HYPERVISOR_set_trap_table`, enables IRQ handling, and installs breakpoint/page-fault/double-fault handlers.
- `trap` routes event-channel IRQs, user exceptions, page faults, diagnostics, and notify/kexit handling.
- `fault386` reads CR2 from Xen shared vcpu info, optionally syncs kernel mappings, then calls VM `fault`.
- `syscall` is called directly from assembly and invokes `dosyscall`.
- `notify`/`noted` implement Plan 9 note delivery and validation of user segment selectors.
- Fork/exec/debug helpers initialize or inspect saved `Ureg` state.
- Safe page-fault handler hooks exist for failsafe callback but currently panic.

Integration:
- Depends on `l.s` vector table, `plan9l.s` syscall entry, Xen shared info, and generic Plan 9 VM/process code.

Risks/notes:
- Safe page-fault support is incomplete.
- Some CR/MSR dumping is deliberately skipped under Xen.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/uartxen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/uartxen.c

Xen console ring as a Plan 9 UART.

Purpose:
- Adapts Xen console shared ring and event channel to Plan 9 UART/console interfaces.

Key behavior:
- Maps console ring at `XENCONSOLE` and records event channel from `start_info`.
- `xenuartputs` and `xenputc` write directly to the console output ring and notify backend.
- `interrupt` consumes input ring bytes and feeds `uartrecv`.
- `kick` drains Plan 9 serial output queue into Xen console ring.
- UART parameter methods accept only supported virtual-console settings.
- `kbdenable` enables console input when `console=0` is configured.

Integration:
- Used by early Xen `main()` for console output and later by Plan 9 UART/keyboard console paths.

Risks/notes:
- Output is dropped when the Xen console ring is full.
- Console settings are mostly nominal; real serial hardware controls are no-ops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/uartxen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm.h

Imported Xen public ARM architecture ABI header.

Purpose:
- Defines ARM Xen guest interface details for hypercalls, guest handles, vCPU register context, and PSR bits.

Key content:
- Documents ARM HVC hypercall calling convention and `XEN_HYPERCALL_TAG`.
- Defines ARM guest-handle unions and handle setters with 64-bit alignment rules.
- Defines `vcpu_guest_core_regs`, `vcpu_guest_context`, `arch_vcpu_info`, `arch_shared_info`, and callback type.
- Lists AArch32/AArch64 PSR mode values and interrupt/mode flags.

Integration:
- Part of Xen public ABI headers included or transformed for Plan 9 Xen support.

Risks/notes:
- ABI layout must remain compatible with Xen; local edits would risk hypercall/control-structure mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm/hvm/save.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm/hvm/save.h

Imported Xen public ARM HVM save header stub.

Purpose:
- Reserves the ARM HVM save-state header include guard and license block.

Key content:
- Contains no ARM HVM save structures in this snapshot, only guard `__XEN_PUBLIC_HVM_SAVE_ARM_H__`.

Integration:
- Present for ABI completeness and include compatibility with Xen public header hierarchy.

Risks/notes:
- Consumers should not expect ARM HVM save records from this file as imported here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm/hvm/save.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/cpuid.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/cpuid.h

Imported Xen public x86 CPUID interface definitions.

Purpose:
- Defines Xen identification CPUID leaves and feature flags.

Key content:
- Xen CPUID leaf base `0x40000000` and `XEN_CPUID_LEAF`.
- Signature values for `XenVMMXenVMM`.
- Documents version and feature leaves.
- Defines feature bit for `MMU_PT_UPDATE_PRESERVE_AD`.

Integration:
- Used by Xen-aware x86 code to detect/paraphrase hypervisor capabilities.

Risks/notes:
- Pure ABI header; values are externally defined by Xen.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/cpuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/hvm/save.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/hvm/save.h

Imported Xen public x86 HVM save-state ABI definitions.

Purpose:
- Defines structures and save-type records used by Xen to save/restore HVM domain CPU and device-model state.

Key content:
- Save file magic/version and `hvm_save_header`.
- CPU register/control/debug/MSR/FPU state structures, including compatibility forms.
- Device-state structures for vPIC, vIOAPIC, LAPIC, PCI IRQ routing, ISA IRQs, PIT, RTC, HPET, PM timer, MTRR, XSAVE, Viridian, VMCE, and TSC adjust.
- Defines save type codes and maximum code.

Integration:
- Public ABI reference in Xen header tree; not directly part of Plan 9 filesystem logic but supports virtualization interface completeness.

Risks/notes:
- Struct packing/layout must track Xen ABI exactly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/hvm/save.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-mca.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-mca.h

Imported Xen public x86 Machine Check Architecture ABI header.

Purpose:
- Defines Xen MCA hypercall interface, event flags, machine-check info records, recovery actions, and injection commands.

Key content:
- MCA interface version, urgent/nonurgent/ack flags, result codes, and `VIRQ_MCA`.
- Record types for global, bank, extended MSR, recovery, and logical CPU machine-check information.
- `mc_info` container and lookup macros for iterating typed records.
- Hypercall command structures for fetch, notifydomain, physcpuinfo, MSR injection, MCE injection, and v2 injection.
- Top-level `xen_mc` command union.

Integration:
- Public Xen ABI support header; relevant for privileged tooling or machine-check event handling, not actively used by the small frontend files in this batch.

Risks/notes:
- Macro iteration depends on trusted record sizes from Xen; consumers should validate inputs if exposed to untrusted domains/tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-mca.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_32.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_32.h

Imported Xen public 32-bit x86 guest ABI header.

Purpose:
- Defines 32-bit Xen hypercall convention, flat segment selectors, hypervisor/machine-to-physical virtual windows, guest handles, user-register context, and callbacks.

Key content:
- Documents hypercall page calling convention using x86 registers.
- Defines Xen flat ring 1/ring 3 selectors used by the Plan 9 Xen port as kernel/user selectors.
- Provides PAE and non-PAE hypervisor and machine-to-physical mapping bounds.
- Defines guest-handle forms for tool/control interfaces.
- Defines `cpu_user_regs`, CR3 PFN packing/unpacking helpers, `arch_vcpu_info` with `cr2`, and `xen_callback`.

Integration:
- Directly informs `mem.h`, `trap.c`, `mmu.c`, and `plan9l.s` segment and trap assumptions.

Risks/notes:
- Selector and mapping constants are ABI-sensitive; mismatches would break trap return, user/kernel segmentation, or MMU setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-x86_32.h -->