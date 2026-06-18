# Research: subset-b-000730

Grouped research for MIPS architecture headers under `sources/distributed-fs/ceph-client`. Each section preserves the exact source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rb.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rb.h

Purpose: RouterBOARD/IDT RC32434 board definitions for memory-mapped registers, GPIO latch bits, external device windows, and board-local device bookkeeping. The header is a low-level platform contract for RC32434 board code and drivers, not a standalone implementation.

Important APIs/types/functions: `REGBASE`, `IDT434_REG_BASE`, `UART0BASE`, `DEV{0..3}{BASE,MASK,C,TC}`, `BTCS`, and `BTCOMPARE` describe register offsets. `LO_WPX`, `LO_ALE`, `LO_CLE`, `LO_CEX`, `LO_FOFF`, `LO_SPICS`, and `LO_ULED` name latch lines. `struct dev_reg` models a base/mask/control/timing register bank. `struct korina_device` carries an Ethernet name, MAC address, and `net_device`. `struct mpmc_device` stores latch/controller state, a spinlock, and an I/O base. `set_latch_u5()` and `get_latch_u5()` are external latch accessors.

Control flow, state, and persistence: The header exposes shared MMIO layout and volatile latch state; control flow lives in platform code that maps `KSEG1ADDR(REGBASE)` and calls the latch helpers. State persists only in device registers and `mpmc_device.state`, guarded by `mpmc_device.lock`.

Dependencies and integration: It depends on MIPS `KSEG1ADDR`, Linux `u32`, `spinlock_t`, `__iomem`, and networking types supplied by including code. It integrates with NAND/SPI/LED control, Korina Ethernet, and RC32434 platform setup.

Risks and test signals: Hard-coded physical offsets make this sensitive to SoC variants. Test by compiling the RC32434 platform, validating latch bit transitions on hardware, and checking Ethernet/NAND boot paths that consume `korina_device` and device window registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rc32434.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rc32434.h

Purpose: Minimal RC32434 CPU helper header. It defines the platform clock multiplier and a pipeline synchronization helper.

Important APIs/types/functions: `IDT_CLOCK_MULT` is fixed to `2`, used by board timing or clock derivation code. `rc32434_sync()` emits a MIPS `sync` instruction through inline assembly.

Control flow, state, and persistence: There is no persistent software state. The only execution behavior is a memory/order synchronization barrier when callers need posted writes or CPU pipeline effects completed before continuing.

Dependencies and integration: Includes `<linux/delay.h>` and `<linux/io.h>`, which suggests use from board setup and low-level I/O code. The helper integrates with the same RC32434 platform layer as `rb.h` and timer definitions.

Risks and test signals: The inline assembly has architecture-visible ordering effects; replacing it with a weaker barrier would risk MMIO ordering bugs. Test signals are RC32434 platform build coverage and runtime stability around register programming, reset, or device init sequences that require `sync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rc32434.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/timer.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/timer.h

Purpose: Timer register layout and bit definitions for RC32434. It describes three counters plus a real-time counter block.

Important APIs/types/functions: `TIMER0_BASE_ADDR` is `0x18028000`; `TIMER_COUNT` is `3`. `struct timer_counter` provides `count`, `compare`, and `ctc`. `struct timer` contains an array of counters plus real-time `rcount`, `rcompare`, and `rtc`. Bit and mask macros include `RC32434_CTC_EN_BIT`, `RC32434_CTC_TO_BIT`, `RC32434_RTC_CE_BIT`, `RC32434_RTC_TO_BIT`, `RC32434_RTC_RQE_BIT`, `RC32434_RCOUNT_MSK`, and `RC32434_RCOMP_MSK`.

Control flow, state, and persistence: The header has no functions; platform timer code maps the register block, writes enable/compare fields, and consumes timeout bits. State persists in hardware counters and compare registers.

Dependencies and integration: It includes `mach-rc32434/rb.h` for `BIT_TO_MASK`. It integrates with clocksource/clockevent setup and interrupt handling for RC32434 timer IRQs.

Risks and test signals: Incorrect masks or counter array sizing will break timer interrupts and scheduling. Test by booting the platform, confirming periodic tick or clockevent programming, and checking timeout bits clear as expected under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rm/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rm/cpu-feature-overrides.h

Purpose: Compile-time CPU feature overrides for SNI RM200 C systems, known to ship with R4600 V2.0 and R5000 processors. It lets generic MIPS code constant-fold feature checks.

Important APIs/types/functions: Defines `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_llsc`, and `cpu_has_64bits` as present. It disables watchpoints, MIPS16, DSP, MIPS MT, userlocal, EJTAG, machine check, prefetch, and MIPS32/64 release-level flags. `cpu_has_dc_aliases` depends on `PAGE_SIZE < 0x4000`.

Control flow, state, and persistence: No runtime state is stored. The macros alter compile-time branches and static keys in architecture code.

Dependencies and integration: Consumers are generic MIPS CPU feature logic, cache/TLB code, signal/FPU setup, and exception paths. It requires `PAGE_SIZE` from page configuration.

Risks and test signals: A wrong override silently compiles in invalid instructions or omits required workarounds. Test with RM200 defconfig builds, FPU and cache-alias stress, and runtime `/proc/cpuinfo` or boot logs matching expected R4x00/R5000 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rm/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-sibyte/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-sibyte/cpu-feature-overrides.h

Purpose: Compile-time feature profile for SiByte MIPS64 processors with a fixed platform configuration.

Important APIs/types/functions: It marks watch registers, vectored interrupts (`cpu_has_divec`), prefetch, machine check, EJTAG, LL/SC, virtual-tag I-cache, 64-bit support, MIPS32r1, and MIPS64r1 as present. It disables MIPS16, VCE, cache CDEX, aliases, DSP, MIPS MT, userlocal, no-FPU-exception mode, and later release flags. It fixes D/I/S-cache line sizes to 32 bytes and marks primary caches non-inclusive.

Control flow, state, and persistence: Feature macros have no runtime state but steer generic branches for cache management, exception vectors, and instruction availability.

Dependencies and integration: Used by the MIPS CPU feature framework, cache code, TLB setup, and SiByte platform builds.

Risks and test signals: Since many paths become constants, any mismatch between SoC revision and macro values can become a boot-time or data-corruption fault. Test by building SiByte kernels, exercising cache flushes and LL/SC atomics, and verifying machine-check/EJTAG paths are not incorrectly assumed absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-sibyte/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/cpu-feature-overrides.h

Purpose: TX49xx platform CPU feature override header for Toshiba/TX49-family MIPS64 systems.

Important APIs/types/functions: Declares LL/SC and 64-bit support present, primary caches non-inclusive, and disables MIPS16, MDMX, MIPS-3D, SmartMIPS, virtual-tag I-cache, I-cache-fill-from-D-cache behavior, DSP/DSP2, MIPS MT, userlocal, and MIPS32/64 release 1/2 feature flags.

Control flow, state, and persistence: No state. The defines specialize generic MIPS code at compile time, especially CPU feature tests around atomics, cache handling, signal/FPU code, and instruction selection.

Dependencies and integration: Consumed by `cpu-features.h` and platform builds using `asm/mach-tx49xx`. Related TX49xx headers in this subset provide I/O mapping, DMA alignment, endian I/O swabbing, and virtual address layout.

Risks and test signals: Incorrectly enabling release-level features or DSP would compile instructions unsupported by older TX49 cores. Test with TX49xx defconfig builds, boot logs, atomic and cache tests, and driver I/O validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/ioremap.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/ioremap.h

Purpose: TX49xx platform hook for direct-mapping a small high physical address window instead of allocating a normal `ioremap` mapping.

Important APIs/types/functions: `plat_ioremap(offset, size, flags)` returns the direct-cast I/O pointer when `offset` falls inside `[TXX9_DIRECTMAP_BASE, TXX9_DIRECTMAP_BASE + 0x400000)`, with the base set to `0xfff000000ul` on 64-bit and `0xff000000ul` on 32-bit. `plat_iounmap(addr)` returns true for addresses in the direct-mapped region.

Control flow, state, and persistence: The functions are stateless. Control flow is a range check followed by either a cast or `NULL`, letting generic `ioremap` continue when the platform hook does not claim the address.

Dependencies and integration: Uses `phys_addr_t`, `__iomem`, and the MIPS `ioremap` platform hook mechanism. It aligns with TX49xx physical memory maps and fixed `FIXADDR_TOP` from `spaces.h`.

Risks and test signals: The `(unsigned long)(int)` casts intentionally preserve 32-bit direct-map forms but are easy to break during cleanup. Test by booting TX49xx, mapping board registers in the direct region, and ensuring `iounmap` does not free direct mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/ioremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/kmalloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/kmalloc.h

Purpose: TX49xx allocation-alignment policy for DMA-safe `kmalloc` allocations.

Important APIs/types/functions: Defines `ARCH_DMA_MINALIGN` as `L1_CACHE_BYTES`, forcing allocations that may be used for DMA to align at least to a cache line.

Control flow, state, and persistence: No control flow or state; it affects allocator constants at compile time.

Dependencies and integration: Requires `L1_CACHE_BYTES` from cache geometry headers. It integrates with Linux slab/kmalloc alignment rules and TX49xx DMA/cache coherency behavior.

Risks and test signals: Too-small alignment can cause DMA cacheline sharing corruption; too-large alignment wastes memory. Test with TX49xx DMA-capable drivers, network/storage I/O, and cache coherency stress under small allocation sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/kmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/mangle-port.h

Purpose: TX49xx port and memory I/O byte-order policy. It tells generic I/O accessors how to swizzle addresses and byte-swap port values.

Important APIs/types/functions: `__swizzle_addr_{b,w,l,q}` are identity mappings. `ioswabb` and `__mem_ioswabb` return byte values unchanged. `ioswabw`, `ioswabl`, and `ioswabq` convert little-endian port values with `le16_to_cpu`, `le32_to_cpu`, and `le64_to_cpu`; memory forms for word/long/quad are identity.

Control flow, state, and persistence: Pure macro transformations, no state. The control behavior is compile-time substitution in generic `in*`, `out*`, and memory I/O helpers.

Dependencies and integration: Depends on Linux endian helpers and sparse `__force` casts. It integrates with MIPS `io.h` and board drivers expecting little-endian PCI/port data.

Risks and test signals: Wrong endian policy corrupts device register values only on affected access widths. Test by exercising PCI/IDE/network register access on TX49xx and comparing raw register dumps against expected little-endian device specifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/spaces.h

Purpose: TX49xx virtual address layout override.

Important APIs/types/functions: Defines `FIXADDR_TOP` as `((unsigned long)(long)(int)0xfefe0000)` before including generic MIPS spaces. The cast preserves a sign-extended 32-bit fixed-address top on relevant builds.

Control flow, state, and persistence: No runtime behavior. This header changes address constants used to lay out fixmap and kernel virtual regions.

Dependencies and integration: Includes `asm/mach-generic/spaces.h` after defining the platform override. It integrates with fixmap, ioremap, highmem, and early boot virtual memory setup.

Risks and test signals: Address-layout mistakes can overlap fixed mappings with other kernel regions or break early I/O mappings. Test by building TX49xx, validating boot-time memory layout messages, and exercising fixmap users such as early console or PCI setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/machine.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/machine.h

Purpose: Generic MIPS machine descriptor and FDT fixup interface. It lets platform code register machine matchers in a linker section and apply device-tree fixups during early boot.

Important APIs/types/functions: `struct mips_machine` contains OF match table, optional FDT pointer, `detect`, `fixup_fdt`, and `measure_hpt_freq` callbacks. `MIPS_MACHINE(name)` places descriptors in `.mips.machines.init`. `for_each_mips_machine(mach)` iterates between `__mips_machines_start` and `__mips_machines_end`. `mips_machine_is_compatible()` checks root-node compatible strings using `fdt_node_check_compatible`. `struct mips_fdt_fixup` and `apply_mips_fdt_fixups()` define fixup execution.

Control flow, state, and persistence: Descriptor state is static init data. Boot code iterates the linker section, checks compatibility or detect callbacks, and optionally mutates an FDT output buffer through ordered fixups.

Dependencies and integration: Depends on libfdt and Open Firmware IDs. It integrates with MIPS generic board boot, device-tree selection, and high-precision timer frequency measurement.

Risks and test signals: Section placement and sentinel bounds are linker-script sensitive. Test with multiple machine descriptors, malformed FDTs, and fixup failure paths that should return `-errno` with useful descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818-time.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818-time.h

Purpose: MIPS wrapper for reading time from an MC146818-compatible CMOS RTC when the shared RTC library is enabled.

Important APIs/types/functions: `mc146818_get_cmos_time()` is defined under `CONFIG_RTC_MC146818_LIB`. It calls `mc146818_get_time(&tm, 1000)`, logs an error and returns `0` on failure, and converts `struct rtc_time` to `time64_t` using `rtc_tm_to_time64()`.

Control flow, state, and persistence: Control flow is a single RTC read with a timeout budget, followed by conversion. Persistent state resides in RTC hardware, not this header.

Dependencies and integration: Depends on `<linux/mc146818rtc.h>` and `<linux/time.h>`. It integrates with MIPS time initialization and board RTC support such as Malta.

Risks and test signals: Returning `0` on read failure maps to the Unix epoch and can hide hardware access issues if callers do not check logs. Test with RTC library enabled/disabled, simulated read failure, and boot-time wall-clock initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818rtc.h

Purpose: Architecture include shim for MC146818 RTC access.

Important APIs/types/functions: It includes `<mc146818rtc.h>` and provides no additional MIPS-specific functions or state.

Control flow, state, and persistence: None in this header. Runtime behavior is entirely supplied by the included generic or platform RTC definitions and the RTC hardware.

Dependencies and integration: It is used where code expects `asm/mc146818rtc.h` to provide machine-dependent RTC access. It connects board code to generic CMOS RTC definitions.

Risks and test signals: The main risk is include-path ambiguity because this shim relies on the correct `<mc146818rtc.h>` being selected. Test by compiling board configurations that include this path and verifying CMOS read/write helpers resolve without duplicate definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/bonito64.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/bonito64.h

Purpose: Bonito64 system-controller register map for MIPS evaluation boards. It provides physical address ranges, PCI config and memory windows, GPIO/interrupt control, DMA/copier registers, and bit encodings.

Important APIs/types/functions: In C, `BONITO(x)` dereferences `_pcictrl_bonito + x` as volatile `u32`; assembly gets offsets. Externs `_pcictrl_bonito` and `_pcictrl_bonito_pcicfg` supply mapped bases. Major groups include boot/flash/socket/PCI address ranges, `BONITO_PCI*` config registers, `BONITO_BONPONCFG`, `BONITO_BONGENCFG`, `BONITO_IODEVCFG`, `BONITO_SDCFG`, `BONITO_PCIMAP`, interrupt registers, mailbox registers, LDMA/copier registers, GPIO helpers, ICU bits, PCI map helpers, and `BONITO_PCITOPHYS()`.

Control flow, state, and persistence: The header has no functions but its lvalue macros perform volatile MMIO reads/writes. Hardware state persists in Bonito registers controlling PCI address translation, cache behavior, interrupts, GPIO, DMA, and DRAM config.

Dependencies and integration: Consumed by MIPS board setup, PCI host bridge code, interrupt controllers, and early platform initialization. It relies on correct initialization of `_pcictrl_bonito`.

Risks and test signals: Volatile lvalue macros make accidental multiple evaluation or read-modify-write bugs likely. Some address translation macros require exact bitfield use. Test with Bonito64 PCI enumeration, interrupt delivery, GPIO access, and DMA/copy engine paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/bonito64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/generic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/generic.h

Purpose: Shared constants for MIPS Technologies evaluation boards, including display registers, revision IDs, system-controller IDs, and PCI BIOS setup hook.

Important APIs/types/functions: Defines `ASCII_DISPLAY_WORD_BASE`, `ASCII_DISPLAY_POS_BASE`, `MIPS_REVISION_REG`, many `MIPS_REVISION_CORID_*` values, artificial `CORE_EMUL_*` IDs, `MIPS_REVISION_CORID`, system-controller IDs such as `MIPS_REVISION_SCON_SOCITSC`, negative legacy SCON values, and `MIPS_REVISION_SCONID`. Declares `mips_revision_sconid`. If `CONFIG_PCI` is set, declares `mips_pcibios_init()`, otherwise defines it as a no-op.

Control flow, state, and persistence: `MIPS_REVISION_CORID` and `MIPS_REVISION_SCONID` map and dereference the revision register through `ioremap` macro expressions. Persistent board identity is in hardware revision registers and cached in `mips_revision_sconid`.

Dependencies and integration: Includes address-space, byte-order, and Bonito definitions. It integrates with Malta/SEAD board setup, PCI host selection, and early display/debug output.

Risks and test signals: Macros that call `ioremap` inside expressions can leak mappings or be unsafe if used repeatedly. Test by booting multiple board controller variants and checking revision/controller detection and PCI init selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/launch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/launch.h

Purpose: Shared secondary-CPU launch mailbox layout for MIPS evaluation boards.

Important APIs/types/functions: C code sees `struct cpulaunch` with `pc`, `gp`, `sp`, `a0`, padding to avoid cacheline thrashing, and `flags`. Assembly sees offsets `LAUNCH_PC`, `LAUNCH_GP`, `LAUNCH_SP`, `LAUNCH_A0`, `LAUNCH_FLAGS` and `LOG2CPULAUNCH`. Flag bits are `LAUNCH_FREADY`, `LAUNCH_FGO`, and `LAUNCH_FGONE`. The mailbox base is `CPULAUNCH`, with `NCPULAUNCH` slots and `LAUNCHPERIOD` poll interval.

Control flow, state, and persistence: Boot CPU writes launch parameters and flag transitions; secondary CPUs poll and update flags. State persists in shared memory or firmware-visible launch area.

Dependencies and integration: Used by SMP bring-up assembly and C board code. Its layout must match both C and assembler consumers.

Risks and test signals: Padding, offset, or flag changes can deadlock secondary CPU startup. Test with SMP boot, cache coherency stress during bring-up, and assembly offset checks against `struct cpulaunch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/launch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/malta.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/malta.h

Purpose: Malta board address and peripheral definitions for system controllers, GIC/CPC/GCMP, RTC, SMSC Super I/O, and jumper register access.

Important APIs/types/functions: Defines MSC interrupt-controller base addresses, `MALTA_GT_PORT_BASE`, `MALTA_BONITO_PORT_BASE`, and `MALTA_MSC_PORT_BASE`. Inline helpers `get_gt_port_base()` and `get_msc_port_base()` read controller windows. Defines `GCMP_BASE_ADDR`, `GIC_BASE_ADDR`, `CPC_BASE_ADDR`, `MSC01_BIU_REG_BASE`, `MSC01_SC_CFG_*`, RTC ports `0x70/0x71`, SMSC config registers and values, `SMSC_WRITE`, `MALTA_JMPRS_REG`, and `malta_dt_shim()`.

Control flow, state, and persistence: Inline port-base helpers read MMIO configuration to compute I/O port bases. Board state persists in system-controller registers, Super I/O config space, and jumper hardware.

Dependencies and integration: Includes GT64120, MSC01 PCI, and `ioremap`/`inl`/`outb` accessors indirectly. It integrates with Malta PCI, interrupt, RTC, device-tree shimming, and Super I/O initialization.

Risks and test signals: Controller-specific base selection is fragile across Malta revisions. Test with GT, Bonito, MSC, and SOC-it variants, PCI I/O enumeration, RTC access, GIC/CPC discovery, and Super I/O activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/malta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/maltaint.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/maltaint.h

Purpose: Interrupt number assignments for Malta boards across CPU, MSC01C, and MSC01E interrupt configurations.

Important APIs/types/functions: `MALTA_INT_BASE` starts at zero. CPU interrupt aliases include software interrupts, mailbox pins, I8259A, GIC chained interrupt, SMI, and core high/low lines. `MSC01C_INT_BASE` and `MSC01E_INT_BASE` are `96`, with constants for timer, PCI, software, mailbox, performance counter, and CPU counter interrupts.

Control flow, state, and persistence: No functions or state. These constants drive interrupt mapping tables and chained interrupt setup.

Dependencies and integration: Consumed by Malta IRQ setup, legacy i8259 routing, GIC integration, and MSC01 interrupt-controller code.

Risks and test signals: Off-by-one or base mismatches route interrupts to wrong Linux IRQs. Test by booting Malta variants, verifying timer tick, PCI interrupts, SMI, software IRQs, and GIC chained delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/maltaint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/msc01_pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/msc01_pci.h

Purpose: Register offsets, field encodings, absolute address macros, and raw access helpers for the MIPS System Controller PCI host bridge.

Important APIs/types/functions: Defines offsets for ID, system-controller-to-PCI memory/I/O base/mask/map registers, PCI-to-system masks/maps, interrupt config/status, config address/data, IACK, header registers, BAR0, config, and swap control. Field macros cover hostbridge ID, mapping fields, interrupt bits, config-address bus/device/function/register fields, BAR sizing, enable bits, retry count, and endian swap modes. `_pcictrl_msc` supplies `MSC01_PCI_REG_BASE`; `MSC_WRITE` and `MSC_READ` dereference volatile `u32`.

Control flow, state, and persistence: No function bodies beyond MMIO access macros. Hardware state persists in mapping, config, interrupt, and swap registers that affect PCI enumeration and transactions.

Dependencies and integration: Used by Malta/SOC-it PCI host code, with fixed default bases `MIPS_MSC01_PCI_REG_BASE` and `MIPS_SOCITSC_PCI_REG_BASE`.

Risks and test signals: The header has suspicious aliases for `MSC01_PCI_HEAD12` through `HEAD15` all using `HEAD11_OFS`, which should be reviewed against hardware docs. Test PCI config cycles, BAR sizing, endian swap configuration, and error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/msc01_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/piix4.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/piix4.h

Purpose: Intel PIIX4 southbridge PCI configuration and power-management register definitions used by MIPS boards such as Malta.

Important APIs/types/functions: Defines function 0 PIRQ route control, SERIRQ control, top-of-memory, deterministic latency, and general configuration bits. Function 1 IDE timing registers include primary/secondary decode enable bits. Function 3 PMBA and PMREGMISC define power-management enable. PM I/O offsets define power-button status and suspend control/type bits. `PIIX4_SUSPEND_MAGIC` supplies the special PCI-cycle data.

Control flow, state, and persistence: No code. State lives in PIIX4 PCI config space and PM I/O registers.

Dependencies and integration: Consumed by Malta southbridge, IRQ routing, IDE, and power-off/suspend code.

Risks and test signals: Register offsets are device-specific; incorrect values can disable IRQ routing or IDE decode. Test PCI config writes, PIRQ routing, SERIRQ, IDE detection, power button status, and suspend/poweroff flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/piix4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sead3-addr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sead3-addr.h

Purpose: Physical address map for the MIPS SEAD-3 board.

Important APIs/types/functions: Defines major regions for FPGA registers, SDRAM, SRAM, optional SRAM, boot flash, user expansion, Ethernet, UART channels, PIC32 registers, LCD registers, CPLD switches/LEDs, USB status bits, soft endian register, reset bits, and revision register. Notable constants include `SEAD3_SDRAM`, `SEAD3_FPGA`, `SEAD3_PI_PIC32_USB_STATUS_*`, `SEAD3_CPLD_*`, `SEAD3_UART_CH_0/1`, `SEAD3_ETHERNET`, and `SEAD3_REVISION_REGISTER`.

Control flow, state, and persistence: No functions. Board drivers and setup code use these constants for MMIO accesses; state persists in FPGA/CPLD/PIC32/peripheral registers.

Dependencies and integration: Integrates with SEAD-3 early platform setup, UART, Ethernet, LCD, USB/PIC32 support, and endian selection code.

Risks and test signals: The map uses fixed uncached physical addresses, so wrong constants can crash during early boot or hit the wrong device. Test early console, revision read, LED/switch access, Ethernet, UARTs, and PIC32 USB interrupt/status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sead3-addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sim.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sim.h

Purpose: Simulator control hook for MIPS board simulation environments.

Important APIs/types/functions: Defines simulator command codes `STATS_ON`, `STATS_OFF`, `STATS_CLEAR`, `STATS_DUMP`, `TRACE_ON`, and `TRACE_OFF`. The `simcfg(code)` macro emits inline assembly that loads the command code into `$4`, emits magic word `0x39`, and declares `$4` clobbered.

Control flow, state, and persistence: `simcfg` is a direct simulator escape instruction. Persistent effects are external to Linux, in the simulator’s statistics/trace state.

Dependencies and integration: Used by simulation-specific board/test code. It assumes a simulator that interprets the magic instruction; on real hardware this would be invalid or meaningless.

Risks and test signals: Use outside the intended simulator can fault. Test only under supported simulators by toggling stats/trace and verifying expected simulator output without corrupting register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cm.h

Purpose: Coherence Manager (CM) register interface and helper logic for MIPS CPS systems. It must be included through `mips-cps.h`.

Important APIs/types/functions: Externs include `mips_gcr_base`, `mips_cm_l2sync_base`, `mips_cm_phys_base()`, `mips_cm_l2sync_phys_base()`, `mips_cm_is64`, `mips_cm_is_l2_hci_broken`, `mips_cm_error_report()`, `mips_cm_probe()`, and `mips_cm_update_property()`. Accessor macros generate `read_gcr_*`, `write_gcr_*`, `change_gcr_*`, and redirected/core-local variants. Register groups cover GCR config/base/access/revision/errors, L2 sync, GIC/CPC base/status, region masks, L2 cache/prefetch/tag/ECC controls, reset/BEV, core coherence/config/other/reset/id fields. Helpers include `mips_cm_present()`, `mips_cm_has_l2sync()`, `mips_cm_l2sync()`, `mips_cm_revision()`, `mips_cm_max_vp_width()`, `mips_cm_vp_id()`, and locked access to other cores/clusters.

Control flow, state, and persistence: Probe code establishes MMIO bases. Inline helpers conditionally read registers, perform L2 sync via MMIO write, compute VP IDs, and route redirected register windows under locks. Persistent state is hardware CM configuration and exported base pointers.

Dependencies and integration: Depends on CPS accessors, bitfield helpers, CPU topology, and optional `CONFIG_MIPS_CM`. It integrates with cache coherency, SMP bring-up, GIC/CPC discovery, L2 operations, and device-tree properties.

Risks and test signals: Mixed 32/64-bit register access through `mips_cm_is64` and redirected-region locking are high risk. Test CM2/CM3/CM3.5 variants, SMP hotplug, L2 sync, GIC/CPC base discovery, and cache error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cpc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cpc.h

Purpose: Cluster Power Controller register interface for MIPS CPS platforms. It is included through `mips-cps.h`.

Important APIs/types/functions: Exposes `mips_cpc_base`, `mips_cpc_default_phys_base()`, `mips_cpc_probe()`, and `mips_cpc_present()`. Accessor macros generate global, core-local, and core-other register accessors. Registers include CPC access, sequencer delays, rail/reset timing, revision, CM power-up control, mirrored config, endianness system config, core command, state/config, other-core select, VP stop/start/running, and per-core config. Lock helpers `mips_cpc_lock_other()` and `mips_cpc_unlock_other()` guard redirected core access when `CONFIG_MIPS_CPC` is enabled.

Control flow, state, and persistence: Probe maps CPC registers; callers issue core power commands and VP run/stop commands through generated accessors. Persistent state is in CPC hardware and exported base pointer.

Dependencies and integration: Depends on CPS accessors and CM locking. It integrates with SMP hotplug, power management, cluster bring-up, and multi-cluster topology code.

Risks and test signals: Power-state command sequencing can hang cores if issued to the wrong redirected core or without locks. Test core power-up/power-down/reset, VP stop/run, endian configuration, and CPC absence paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cps.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cps.h

Purpose: Top-level MIPS Coherent Processing System helper header. It defines common MMIO accessor generators, includes CM/CPC/GIC register interfaces, and provides topology helpers.

Important APIs/types/functions: `CPS_ACCESSOR_A/R/W/M/RO/WO/RW` create address, read, write, change, set, and clear helpers with 32/64-bit handling. `__cps_access_bad_size()` catches invalid accessor sizes at compile time. Topology helpers include `mips_cps_numclusters()`, `mips_cps_cluster_config()`, `mips_cps_numcores()`, `mips_cps_numiocu()`, `mips_cps_numvps()`, `mips_cps_multicluster_cpus()`, and `mips_cps_first_online_in_cluster()`.

Control flow, state, and persistence: Accessors route through `mips_<unit>_base` and use `mips_cm_is64` to split 64-bit accesses on 32-bit GCR windows. Topology helpers read CM/CPC registers, sometimes under redirected-region locks. No persistent state is introduced beyond hardware register state.

Dependencies and integration: Depends on bitfield, cpumask, I/O, CPU topology, and the included `mips-cm.h`, `mips-cpc.h`, and `mips-gic.h`. It integrates with SMP topology, interrupt routing, power management, and cache coherency.

Risks and test signals: The 64-bit split read/write order and multi-cluster redirect logic are correctness-critical. Test across CM revisions, 32/64-bit kernels, multi-VP cores, multi-cluster systems, and absent-CM fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-gic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-gic.h

Purpose: MIPS Global Interrupt Controller register interface and local interrupt definitions. It is included via `mips-cps.h`.

Important APIs/types/functions: Exposes `mips_gic_base` and `mips_gic_present()`. Accessor macros generate shared, local VP, redirected, per-interrupt register, and bit-per-interrupt helpers. Register groups cover shared config/counter, polarity/trigger/dual-edge, wedge, masks/pending, interrupt-to-pin and interrupt-to-VP maps, local VP control/pending/mask/map/other/ident/compare, and EIC shadow sets. `enum mips_gic_local_interrupt` lists watchdog, compare, timer, performance counter, software interrupts, FDC, and count. `mips_gic_vx_map_reg()` maps enum order to map-register index. Externs return virqs for CP0 compare, perfcount, and FDC interrupts.

Control flow, state, and persistence: Inline bit accessors select 32-bit or 64-bit register lanes based on `mips_cm_is64`. Persistent state is interrupt routing, masks, pending bits, and counter/compare state in GIC hardware.

Dependencies and integration: Uses CPS accessors and Linux bitops. Integrates with irqchip code, clockevents, perf, FDC, SMP IPI/local interrupt routing, and EIC mode.

Risks and test signals: Bit-lane math, FDC map index special-casing, and redirected VP access are high-risk. Test shared IRQ polarity/trigger configuration, local timer/perf/FDC virqs, IPI/software interrupts, EIC shadow routing, and 32/64-bit GIC windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-gic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-r2-to-r6-emul.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-r2-to-r6-emul.h

Purpose: Interface for emulating removed or changed MIPS Release 2 instructions on Release 6 CPUs.

Important APIs/types/functions: `struct mips_r2_emulator_stats` and `struct mips_r2br_emulator_stats` record per-instruction emulation counts when `CONFIG_DEBUG_FS` is enabled. `MIPS_R2_STATS(M)` and `MIPS_R2BR_STATS(M)` enumerate statistic fields or compile to no-ops. `struct r2_decoder_table` maps instruction masks and encodings to handler functions. Exposes `do_trap_or_bp()`, `mipsr2_decoder()`, `mipsr2_emulation`, and `NO_R6EMU`.

Control flow, state, and persistence: On a reserved-instruction/trap path, decoder code matches instruction words against tables, invokes handlers, updates optional debugfs stats, and can raise trap/breakpoint signals. State includes `mipsr2_emulation` policy and debug counters.

Dependencies and integration: Depends on `struct pt_regs`, signal/trap handling, debugfs configuration, CPU feature macros, and R6 exception paths.

Risks and test signals: Incorrect decode masks can emulate the wrong instruction or skip needed traps. Test with R6 kernels running R2 user binaries, debugfs stat increments, disabled-emulation `NO_R6EMU` behavior, and signal delivery for unhandled instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-r2-to-r6-emul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips_mt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips_mt.h

Purpose: Public MIPS MT configuration and sysfs-class declarations.

Important APIs/types/functions: Exposes `tclimit`, `vpelimit`, `mt_fpu_cpumask`, `mt_fpemul_threshold`, `mips_mt_set_cpuoptions()`, and `mt_class` when relevant. If `CONFIG_MIPS_MT` is absent, `mips_mt_set_cpuoptions()` compiles to a no-op.

Control flow, state, and persistence: The header itself has no implementation. Global state controls thread-context and VPE limits, FPU CPU mask, and FPU emulation threshold for MIPS MT systems.

Dependencies and integration: Depends on Linux `cpumask_t` and class declarations. It integrates with MIPS MT boot setup, sysfs exposure, FPU policy, and scheduler/CPU option initialization.

Risks and test signals: Misconfigured TC/VPE limits can expose nonexistent hardware contexts or underuse available ones. Test MIPS MT boot, sysfs class registration, FPU affinity/emulation behavior, and non-MT build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mips_mt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsmtregs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsmtregs.h

Purpose: CP0 register definitions and inline instruction wrappers for MIPS Multi-Threading (VPE/TC) control.

Important APIs/types/functions: Provides read/write macros for MVPControl/MVPConf, VPEControl/VPEConf, TCStatus/TCBind/TCHalt/TCContext, plus assembly register names. Bitfields define MVP enable, VPE targeting, TC states, VPE/TC configuration, halt flags, and thread exception codes. Runtime helpers include `core_nvpes()`, `dvpe()`, `evpe()`, `dmt()`, `emt()`, `ehb()`, `mftc0()`, `mftgpr()`, `mftr()`, `mttgpr()`, `mttc0()`, `mttr()`, `settc()`, and numerous targeted VPE/TC CP0/GPR access macros. It also builds set/clear/change helpers for `mvpcontrol`.

Control flow, state, and persistence: Helpers emit MIPS MT instructions, use execution hazard barriers, and require callers to set a target TC before targeted access. State persists in CP0 MT registers and selected target TC/VPE context.

Dependencies and integration: Builds on `mipsregs.h`, CPU feature `cpu_has_mipsmt`, ISA-level macros, and toolchain fallback instruction encodings. Used by SMP/MT bring-up, hotplug, and low-level scheduler code.

Risks and test signals: Targeted TC operations are ordering-sensitive; missing `ehb` or wrong target can corrupt another thread context. Test VPE enable/disable, TC halt/restart, secondary thread startup, non-MT fallback, and microMIPS/toolchain fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsmtregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsprom.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsprom.h

Purpose: Numeric PROM service call identifiers for legacy MIPS firmware interfaces.

Important APIs/types/functions: Defines service numbers such as `PROM_RESET`, `PROM_EXEC`, `PROM_RESTART`, `PROM_REINIT`, `PROM_REBOOT`, `PROM_AUTOBOOT`, `PROM_OPEN`, `PROM_READ`, `PROM_WRITE`, `PROM_IOCTL`, `PROM_CLOSE`, character/string I/O, packet operations, and VME-style read-modify-write operations.

Control flow, state, and persistence: No functions or state. Firmware call wrappers use these constants to dispatch into PROM services; persistent effects are firmware/device dependent.

Dependencies and integration: Integrated with legacy PROM console, boot, device, network, and reset code on systems that still expose this service table.

Risks and test signals: The comments mark several services as unclear; wrong numbers can invoke destructive firmware operations. Test only under matching firmware or emulator by validating benign console and query services before reset/reboot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsregs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsregs.h

Purpose: Central MIPS CP0/CP1 register, bitfield, instruction, and TLB operation header. It is a foundational architecture interface used across exception handling, MMU, cache, FPU, virtualization, DSP, and CPU feature code.

Important APIs/types/functions: Defines CP0 register names/selects, EntryLo/PageMask/PageGrain/EntryHi/status/cause/config/watch/perf/MAAR/EBase/segmentation/page-walker/guest-control/CDMM/FPU constants, exception codes, and ISA mode helpers. Inline/macro APIs include `mm_insn_16bit()`, raw instruction emitters, assembler macro generators, `tlbinvf()`, R10000 performance counter helpers, generic CP0 read/write primitives for 32/64/ulong and high-half XPA access, hundreds of `read_c0_*`/`write_c0_*` and guest `read_gc0_*`/`write_gc0_*` wrappers, CP1 control access, DSP accumulator/control access, TLB operations, guest TLB operations, set/clear/change builders, and `get_ebase_cpunum()`.

Control flow, state, and persistence: Most helpers emit inline assembly to read/write processor control registers, with special paths for 32-bit kernels accessing 64-bit CP0 registers under local IRQ disable. TLB helpers require callers to handle hazards. Persistent state is CPU control-register, TLB, guest CP0, FPU, DSP, and page-walker hardware state.

Dependencies and integration: Includes hazards and ISA revision support. It is consumed by nearly all MIPS low-level code: traps, context switch, KVM/VZ, perf, cache/TLB management, FPU/MSA, CPU probing, and platform setup.

Risks and test signals: This header is high blast radius. Risks include wrong register select, missing hazard barriers, fallback instruction encoding mistakes, 32/64-bit split ordering, microMIPS encoding mismatches, and unsafe TLB operations. Test with broad MIPS defconfig builds, boot on multiple ISA revisions, KVM/VZ guest tests, perf/FPU/DSP/MSA tests, TLB stress, and assembler fallback configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmiowb.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmiowb.h

Purpose: MIPS implementation of the MMIO write barrier hook.

Important APIs/types/functions: Defines `mmiowb()` as `wmb()` and then includes `asm-generic/mmiowb.h`.

Control flow, state, and persistence: The macro emits a write memory barrier where generic locking/MMIO code requests ordering of prior MMIO writes. No persistent software state is introduced here.

Dependencies and integration: Depends on `asm/barrier.h` and the generic mmiowb framework. It integrates with driver spinlock-unlock paths and architectures needing explicit posted-write ordering.

Risks and test signals: If `wmb()` is too weak for a platform’s MMIO ordering, drivers can observe device register writes out of order. Test with driver MMIO ordering stress, SMP device access under locks, and architecture barrier litmus tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmiowb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu.h

Purpose: Defines the MIPS `mm_context_t` structure stored in each `mm_struct`.

Important APIs/types/functions: `mm_context_t` contains either per-CPU ASIDs (`u64 asid[NR_CPUS]`) or a global `atomic64_t mmid`, a `vdso` pointer, and delay-slot emulation page tracking: `bd_emupage_lock`, `bd_emupage_allocmap`, and `bd_emupage_queue`.

Control flow, state, and persistence: No functions. The state persists for the lifetime of a process address space and is initialized/cleaned by `mmu_context.h` helpers.

Dependencies and integration: Depends on atomic, spinlock, and waitqueue types. Integrated with ASID/MMID allocation, context switching, VDSO mapping, and branch-delay-slot emulation.

Risks and test signals: The union means code must choose ASID vs MMID paths consistently based on `cpu_has_mmid`. Test process creation/destruction, ASID rollover, MMID-capable CPUs, VDSO access, and branch-delay emulation allocation contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu_context.h

Purpose: MIPS MMU context management for process address spaces, ASID/MMID handling, TLB-miss handler PGD setup, and context switch hooks.

Important APIs/types/functions: `htw_set_pwbase()`, `TLBMISS_HANDLER_SETUP_PGD`, `TLBMISS_HANDLER_RESTORE`, and `TLBMISS_HANDLER_SETUP` configure TLB miss state and hardware page walker base. `MMID_KERNEL_WIRED` reserves MMID 0 for wired kernel entries. Helpers include `asid_version_mask()`, `asid_first_version()`, `cpu_context()`, `set_cpu_context()`, `asid_cache()`, `cpu_asid()`, and declarations for `get_new_mmu_context()`, `check_mmu_context()`, and `check_switch_mmu_context()`. Implements `init_new_context()`, `switch_mm()`, `destroy_context()`, and `drop_mmu_context()`.

Control flow, state, and persistence: `init_new_context()` clears ASID/MMID state and initializes delay-slot emulation tracking. `switch_mm()` disables IRQs, stops HTW, checks/assigns context, updates mm CPU masks, restarts HTW, and restores IRQs. `drop_mmu_context()` either invalidates MMID via GINVT, allocates a new ASID for active mms, or clears inactive per-CPU context.

Dependencies and integration: Depends on cache/TLB flush, HTW, GINVT, hazards, SMP, branch-delay emulation, and generic MM hooks. Integrated with scheduler context switches, TLB miss handlers, KVM entry setup, and process lifecycle.

Risks and test signals: ASID/MMID rollover, HTW stop/start, and GINVT wired-entry reservation are correctness-critical. Test fork/exec/exit stress, ASID rollover, SMP TLB shootdowns, MMID CPUs, hardware page walker paths, KVM entry setup, and delay-slot emulation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmzone.h

Purpose: MIPS memory-zone/NUMA include shim and fallback physical-address-to-node helpers.

Important APIs/types/functions: Includes `asm/page.h`; under `CONFIG_NUMA`, includes `<mmzone.h>`. Provides fallback `pa_to_nid(addr) 0` and `nid_to_addrbase(nid) 0` when not defined elsewhere.

Control flow, state, and persistence: No runtime behavior. The macros make non-NUMA builds report all physical memory as node 0.

Dependencies and integration: Integrated with generic memory-management code that expects `pa_to_nid` and `nid_to_addrbase`. NUMA platforms can override them through included headers.

Risks and test signals: Fallbacks are correct only for non-NUMA or UMA platforms. Test NUMA builds for real overrides, non-NUMA builds for successful memory init, and memory hotplug or node lookup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/module.h

Purpose: MIPS module-loader architecture definitions, including module-specific exception tables and ELF relocation type aliases.

Important APIs/types/functions: `struct mod_arch_specific` stores data-bus-error exception table list/ranges and pending `mips_hi16` relocations. Defines `Elf64_Mips_Rel` and `Elf64_Mips_Rela` with MIPS64 packed relocation fields. For `CONFIG_32BIT` or `CONFIG_64BIT`, aliases generic `Elf_*`, `Elf_Mips_Rel`, `Elf_Mips_Rela`, `ELF_R_TYPE`, `ELF_R_SYM`, `ELF_MIPS_R_SYM`, and `ELF_MIPS_R_TYPE`. Declares or stubs `search_module_dbetables()`.

Control flow, state, and persistence: State is attached to loaded modules for relocation and exception lookup. The DBE table lookup returns matching exception entries for fault recovery.

Dependencies and integration: Depends on Linux ELF types, module code, and MIPS exception tables. Integrates with module relocation, fault handling, and data bus error recovery.

Risks and test signals: MIPS64 relocation packing differs from generic ELF64; incorrect aliases break module loading. Test 32/64-bit module builds, HI16/LO16 relocation sequences, DBE exception table lookup, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/msa.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/msa.h

Purpose: MIPS SIMD Architecture context and control-register interface.

Important APIs/types/functions: Extern assembly helpers save, restore, initialize upper MSA state, and read/write vector registers in byte/half/word/double formats. Inline `read_msa_wr()` and `write_msa_wr()` dispatch by `enum msa_2b_fmt` and `BUG()` on invalid formats. `enable_msa()`, `disable_msa()`, `is_msa_enabled()`, `thread_msa_context_live()`, `save_msa()`, `restore_msa()`, and `init_msa_upper()` manage feature availability and per-thread state. Toolchain fallback macros encode `cfcmsa` and `ctcmsa`; `__BUILD_MSA_CTL_REG` creates read/write helpers for MSA IR, CSR, ACCESS, SAVE, MODIFY, REQUEST, MAP, and UNMAP. Bitfields define MSAIR and MSACSR rounding, flags, enables, causes, NX, and FS.

Control flow, state, and persistence: Enabling/disabling toggles CP0 Config5 MSAEN with FPU hazards. Thread context live state uses `TIF_MSA_CTX_LIVE`. Persistent state is in task FPU/MSA register storage and MSA control registers.

Dependencies and integration: Depends on `mipsregs.h`, `asm/inst.h`, CPU feature `cpu_has_msa`, task flags, FPU hazards, and assembly save/restore routines. Integrates with context switch, signal handling, ptrace, and exception paths.

Risks and test signals: Invalid format handling, hazard ordering, and constant-folded `cpu_has_msa` paths are key risks. Test MSA context switches, signal save/restore, ptrace register access, disabled-MSA exceptions, and toolchains without native MSA mnemonics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/msa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/msc01_ic.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/msc01_ic.h

Purpose: MIPS System Controller interrupt-controller register definitions and board mapping interface.

Important APIs/types/functions: Defines offsets and absolute addresses for reset, enable/disable masks, raw/masked input status, level/RAM shadow configuration, output status, global enable, vector base/current vector, EOI, config, timer reload/current/config, setup lines, and 64-bit mask/status registers. Field macros cover reset, priority level, spurious flag, shadow RAM read/write fields, global enable, timer enable/interrupt/edge, and setup priority/edge. `msc_irqmap_t` maps board IRQ line, type, and level. `MSC01_IRQ_LEVEL`/`MSC01_IRQ_EDGE` classify trigger type. Externs `init_msc_irqs()` and `ll_msc_irq()` initialize and handle low-level dispatch.

Control flow, state, and persistence: Initialization code programs masks, priorities, and trigger modes from board maps. Interrupt handling reads active vector/status and writes EOI. State persists in interrupt-controller registers.

Dependencies and integration: Requires `MSC01_IC_REG_BASE` from board headers such as Malta. Integrated with MIPS IRQ core, MSC01/SOC-it board setup, and timer interrupt delivery.

Risks and test signals: Priority/trigger configuration and vector base errors can lose or storm interrupts. Test timer, PCI, software, edge/level IRQs, EOI behavior, and board-specific IRQ map coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/msc01_ic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/crypto.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/crypto.h

Purpose: Cavium Octeon COP2 crypto instruction interface for MD5, SHA1, SHA256, and SHA512 acceleration.

Important APIs/types/functions: `OCTEON_CR_OPCODE_PRIORITY` is `300`. Externs `octeon_crypto_enable()` and `octeon_crypto_disable()` save/restore COP2 crypto state around use. Macros write/read hash dwords, block dwords, and start hash operations using `dmtc2`/`dmfc2` with fixed COP2 opcodes. MD5 uses big-endian conversion for hash/block writes; SHA1/SHA256 starts write raw values; SHA512 has separate hash/block opcode ranges. The file contains duplicated SHA1/SHA256/SHA512 macro definitions with identical bodies.

Control flow, state, and persistence: Callers enable COP2 crypto, load state/block words through macros, trigger the final operation, read hash output, and disable/restore state. Persistent state is in COP2 crypto registers and saved `octeon_cop2_state`.

Dependencies and integration: Depends on scheduler state, byte-order helpers, `mipsregs.h`, and Octeon crypto drivers.

Risks and test signals: Opcode constants, endian conversions, and duplicate macro definitions are risk points. Test known-answer vectors for MD5/SHA1/SHA256/SHA512, context switches during crypto use, preemption/interrupt safety, and big/little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-address.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-address.h

Purpose: Octeon address decode and address-construction definitions from the Cavium SDK.

Important APIs/types/functions: Enumerations define XKSEG subspaces, kseg3 window decode classes, and DMA window operations. `cvmx_addr_t` is a `uint64_t` union with endian-specific bitfield views for virtual addresses, kuseg/xkseg/xkphys, physical memory and I/O addresses, scratchpad window addresses, IOBDMA window stores, and DID-space filling. Macros include `CVMX_ADD_SEG32`, `CVMX_IO_SEG`, `CVMX_ADD_SEG`, `CVMX_ADD_IO_SEG`, `CVMX_ADDR_DIDSPACE`, `CVMX_ADDR_DID`, `CVMX_FULL_DID`, Octeon device IDs, and full DID/sub-DID constants for packet, tag, FAU, TIM, KEY, PCI, IPD, DFA, MIS, and ZIP access.

Control flow, state, and persistence: No executable functions. Callers construct or decode addresses; persistence is hardware address-space interpretation.

Dependencies and integration: Requires fixed-width integer types and endian bitfield configuration. Integrated with Octeon MMIO/CSR access, boot bus, NCB/IOB DMA, packet/tag engines, and user/kernel XKPHYS I/O mapping.

Risks and test signals: C bitfield layout and endian conditionals are fragile; address-construction mistakes can target the wrong device or memory space. Test CSR address generation, packet/tag device access, IOBDMA stores, scratchpad window access, and both endian build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-address.h -->
