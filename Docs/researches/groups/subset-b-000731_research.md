# Research: subset-b-000731

Grouped source research for subset B work item `subset-b-000731`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-agl-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-agl-defs.h

## Purpose
This generated-style header describes the Octeon AGL/GMX register block used by the single/low-speed Ethernet MAC path. It gives callers CSR addresses and endian-aware bitfield unions for port configuration, receive filtering, frame checks, flow control, statistics, transmit controls, interrupt reporting, and the top-level AGL port control register.

## Important APIs, Types, and Functions
The public surface is macro and union based. `CVMX_AGL_GMX_*` macros build `CVMX_ADD_IO_SEG()` CSR addresses, commonly indexed by `offset & 1` for the two AGL ports. Important register groups include global diagnostics (`BAD_REG`, `BIST`, `DRV_CTL`, `INF_MODE`), per-port mode/config (`PRTX_CFG`, `PRTX_CTL`), receive address CAM registers (`RXX_ADR_CAM0..5`, `RXX_ADR_CAM_EN`, `RXX_ADR_CTL`), receive admission and frame validation (`RXX_DECISION`, `RXX_FRM_CHK`, `RXX_FRM_CTL`, min/max/jabber/IFG/UDD skip), receive and transmit interrupts (`RXX_INT_EN`, `RXX_INT_REG`, `TX_INT_EN`, `TX_INT_REG`), receive backpressure and status (`RX_BP_*`, `RX_PRT_INFO`, `RX_TX_STATUS`), transmit timing/append/threshold/pause/statistics (`TXX_*`, `TX_*`), and source MAC/programmed pause packet registers.

## Control Flow
There is no executable control flow in this file. Driver code selects a CSR macro, reads or writes the corresponding 64-bit register, edits the matching union's `.u64` or `.s` fields, and writes it back. Hardware then controls receive filtering, frame admission, error latching, flow control, and statistic counters.

## State and Persistence Behavior
All state lives in the AGL/GMX hardware CSRs. Configuration writes persist until reset or later driver reconfiguration. Interrupt/status registers are hardware-latched, often cleared by writing status bits. Statistic CSRs accumulate packet/octet/error counters and can be affected by the stats-control fields.

## Dependencies and Integration Points
The header depends on Octeon CSR address helpers and the kernel's endian bitfield convention. It integrates with Octeon Ethernet drivers that program AGL ports, with link/PHY setup through interface mode and in-band status fields, with interrupt handlers through RX/TX interrupt enable/status unions, and with ethtool or diagnostics through statistics CSRs.

## Risks
The field layouts are hardware ABI: using the wrong port offset, wrong chip-generation interpretation, or wrong endian view can silently corrupt MAC configuration. Interrupt enable/status unions contain many specific error bits, so handlers must clear only acknowledged conditions. Statistics and flow-control fields can change link behavior immediately; misprogramming pause, backpressure, or frame-check fields can cause packet loss, bad filtering, or link stalls.

## Test Signals
Build-test Octeon Ethernet configurations that include AGL support. Runtime signals include successful link bring-up on AGL ports, correct programmed MAC filtering, expected RX/TX interrupt causes, sane ethtool counters, pause/backpressure behavior under FPA pressure, and no unexpected `BAD_REG`/BIST/error bits after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-agl-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asm.h

## Purpose
This header centralizes Octeon executive assembly primitives for memory ordering, I/O DMA ordering, cache operations, special prefetch commands, population count, and hardware-register reads. It hides Cavium-toolchain versus generic-assembler differences behind CVMX macros.

## Important APIs, Types, and Functions
Important macros include `CVMX_SYNC`, `CVMX_SYNCW`, `CVMX_SYNCWS`, `CVMX_SYNCS`, string forms for inline assembly, `CVMX_SYNCIOBDMA`, `CVMX_PREPARE_FOR_STORE`, `CVMX_DONT_WRITE_BACK`, `CVMX_ICACHE_INVALIDATE`, `CVMX_ICACHE_INVALIDATE2`, `CVMX_DCACHE_INVALIDATE`, `CVMX_CACHE`, L2 helpers (`CVMX_CACHE_LCKL2`, `CVMX_CACHE_WBIL2`, `CVMX_CACHE_WBIL2I`, `CVMX_CACHE_LTGL2I`), `CVMX_POP`, `CVMX_DPOP`, `CVMX_RDHWR`, and `CVMX_RDHWRNV`.

## Control Flow
There is no C control flow. Each macro emits one or more MIPS/Octeon instructions directly at the caller site. `CVMX_SYNCW` intentionally emits two `syncw` instructions when Octeon instructions are available to work around CN3XXX Core-401 ordering errata; non-Octeon assembler paths fall back to portable `sync`.

## State and Persistence Behavior
The macros do not keep software state. They affect CPU ordering, cache state, prefetch/dirty status, or return transient hardware values. Cache invalidation and L2 operations have system-visible side effects and must be paired with correct address ranges and barriers by callers.

## Dependencies and Integration Points
It depends on `octeon-model.h` and compile-time `__OCTEON__` feature selection. It is included by low-level CVMX code such as FPA, FAU, command queues, packet I/O, and boot paths that need precise ordering around non-coherent bus, scratchpad, cache, and LL/SC operations.

## Risks
These macros are correctness-critical and architecture-specific. Replacing `syncw` sequences, dropping the memory clobber, or using cache op macros on the wrong address can introduce rare SMP ordering bugs, stale instruction/data cache state, or assembler incompatibilities. Deprecated no-op `CVMX_SYNCIO*` forms may mislead new code if it expects real I/O ordering.

## Test Signals
Useful signals are successful MIPS/Octeon builds with and without `__OCTEON__`, SMP stress around FPA/command-queue/FAU operations, instruction patching or generated-code tests after I-cache invalidation, and hardware data-path tests that would expose missing store or IOBDMA barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asxx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asxx-defs.h

## Purpose
This header defines Octeon ASX/ASXX Ethernet interface CSRs. It covers RX/TX port enables, clock and data delay settings, RGMII/GMII/MII loopback and compensation, wake-on-LAN matching, interrupt status/enables, and RLD/FCRAM interface tuning registers.

## Important APIs, Types, and Functions
Address macros include `CVMX_ASXX_RX_PRT_EN`, `CVMX_ASXX_TX_PRT_EN`, `CVMX_ASXX_INT_REG`, `CVMX_ASXX_INT_EN`, RX/TX clock setup arrays, `CVMX_ASXX_PRT_LOOP`, `CVMX_ASXX_TX_HI_WATERX`, WOL registers, GMII/MII data/clock set registers, and RLD tuning registers. `__cvmx_interrupt_asxx_enable(int block)` is declared for interrupt enable integration. Bitfield unions model each CSR, including interrupt bits for overflow, TX/RX pop, and port-level events; loopback enable bits; RX/TX port enable masks; WOL mask/signature/power-ok fields; and RLD drive/control/bypass values.

## Control Flow
The file has no inline logic. Callers compute a block-indexed CSR address, load the matching union, modify fields, and write the CSR. The ASX hardware applies port gating, clock/data delay, loopback, WOL, and interrupt behavior immediately.

## State and Persistence Behavior
State is held by ASX hardware CSRs. Port enables, loopback, high-water, delay, compensation, and WOL settings persist until reset or later writes. Interrupt registers latch hardware conditions and are consumed by interrupt handlers.

## Dependencies and Integration Points
It depends on `CVMX_ADD_IO_SEG()` and Octeon endian bitfield definitions. It integrates with Octeon Ethernet helper code, GMX/IPD/PKO setup, PHY/link management, wake-on-LAN support, and the platform interrupt layer via the declared ASXX interrupt enable helper.

## Risks
Register offsets mask block and lane values, so incorrect block IDs can target the wrong ASX instance. RX/TX timing fields are board- and PHY-sensitive; bad values can produce marginal links rather than obvious failures. WOL and interrupt status fields must be cleared and masked carefully to avoid missed wake events or interrupt storms.

## Test Signals
Build-test drivers that include ASXX definitions. Runtime checks include link stability across RGMII/GMII/MII modes, loopback diagnostics, RX/TX enable transitions, WOL signature behavior, absence of ASXX interrupt storms, and stable packet traffic after clock/data delay changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asxx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-boot-vector.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-boot-vector.h

## Purpose
This header defines the Octeon boot-vector table ABI used to redirect a core after NMI. It gives one vector entry per possible MIPS CPUNum and exposes the lookup function for code that installs per-core secondary entry points.

## Important APIs, Types, and Functions
`OCTEON_BOOT_MOVEABLE_MAGIC1` identifies the movable boot-bus vector code. `struct cvmx_boot_vector_element` contains `target_ptr` plus three application-owned argument slots, `app0`, `app1`, and `app2`. `cvmx_boot_vector_get()` returns the vector table base or `NULL` if the table cannot be obtained.

## Control Flow
Callers obtain the vector table, fill the indexed entry for a target core, then trigger NMI or a boot-vector mechanism. When the vector code runs, it transfers execution to `target_ptr` for that core while preserving most general-purpose registers as described in the file comments.

## State and Persistence Behavior
The vector table is persistent shared boot memory or boot-bus-installed state. Application argument fields remain untouched by vectoring code. The vectoring path clobbers CP0_DESAVE and, on Octeon II and later, CP0_KScratch2; older cores also clobber `k1`.

## Dependencies and Integration Points
It depends on `asm/octeon/octeon.h` and the implementation in `cvmx-boot-vector.c`. It integrates with SMP bring-up, NMI-based core release, crash/debug paths, and bootloader-provided low-level vector code.

## Risks
The table index uses CPUNum, which is not always a compact Linux CPU number on multi-node systems. A bad `target_ptr` or stale argument slot can send a core into invalid code during NMI. Callers must account for documented scratch register clobbering and address-space expectations for kseg0/xkphys target pointers.

## Test Signals
Signals include successful secondary-core release, correct target entry on sparse-core systems, no register corruption beyond documented scratch registers, valid behavior on pre-Octeon-II and newer CPUs, and failure handling when `cvmx_boot_vector_get()` returns `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-boot-vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootinfo.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootinfo.h

## Purpose
This header defines the bootloader-to-kernel/application bootinfo ABI for Octeon. It records memory layout, clocks, board identity, MAC address allocation, boot flags, optional device-tree address, and extended core mask data, with explicit major/minor versioning.

## Important APIs, Types, and Functions
`CVMX_BOOTINFO_MAJ_VER`, `CVMX_BOOTINFO_MIN_VER`, and `CVMX_BOOTINFO_OCTEON_SERIAL_LEN` version and size the ABI. `struct cvmx_bootinfo` is endian-sensitive and contains stack/heap/descriptor addresses, exception base, core mask, DRAM size, bootmem descriptor address, debug flags, eclock/dclock, board type/revision/serial, MAC base/count, compact-flash and LED bases, DFA clock, `config_flags`, FDT address, and `struct cvmx_coremask ext_core_mask`. Config flag macros describe PCI host/target, debug, no-magic, oversized TLB mapping, and break behavior. `enum cvmx_board_types_enum` and `enum cvmx_chip_types_enum` enumerate known board/chip IDs, with `cvmx_board_type_to_string()` and `cvmx_chip_type_to_string()` converting IDs to strings.

## Control Flow
There is no runtime initialization in the header. Early platform code receives or locates a bootinfo block, checks version fields, then reads fields to configure memory, devices, CPU selection, MAC pools, clocks, FDT, and board-specific behavior. String helpers are simple switch statements over enum constants.

## State and Persistence Behavior
The bootinfo block is bootloader-owned ABI data consumed during early boot and often referenced later for board identity and configuration. The structure is append-only for minor-version compatibility; incompatible layout changes require a major version bump. No persistent storage is written by this header.

## Dependencies and Integration Points
It depends on `cvmx-coremask.h`. It integrates with Octeon platform initialization, bootmem setup via `phy_mem_desc_addr`, clock setup, network-device MAC assignment, board-specific drivers, debugger support, FDT discovery, and SMP/core selection.

## Risks
ABI drift is the central risk: changing field order, endian layout, name sizes, or version rules can break bootloader compatibility. The legacy 32-bit `core_mask` is insufficient on high-core or sparse multi-node systems, so code must prefer `ext_core_mask` when available. Board enum string helpers return `NULL` for unsupported board IDs, which callers must tolerate.

## Test Signals
Boot multiple Octeon board types and endian modes. Validate parsed DRAM size, clocks, MAC ranges, FDT address, PCI flags, board strings, and extended core masks. Compatibility tests should boot with older minor bootinfo versions and with unknown board IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootmem.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootmem.h

## Purpose
This header declares Octeon's simple boot-time physical memory allocator and named-block ABI. It is used before normal kernel allocators or by CVMX applications to allocate shared, bootloader-described memory regions.

## Important APIs, Types, and Functions
Constants define the ABI-sized name length, named-block count, minimum alignment, descriptor version, and allocation flags (`END_ALLOC`, `NO_LOCKING`). `struct cvmx_bootmem_block_header` stores free-list links in physical memory. `struct cvmx_bootmem_named_block_desc` describes named allocations. `struct cvmx_bootmem_desc` is the global allocator descriptor with endian-specific field order, lock, free-list head, app-data fields, and named-block array metadata.

Declared APIs include `cvmx_bootmem_init`, address-specific and named allocators (`cvmx_bootmem_alloc_address`, `cvmx_bootmem_alloc_named`, `cvmx_bootmem_alloc_named_range`, `cvmx_bootmem_alloc_named_range_once`), named-block free/find helpers, physical allocation helpers (`cvmx_bootmem_phy_alloc`, `cvmx_bootmem_phy_named_block_alloc`, `__cvmx_bootmem_phy_free`), explicit lock/unlock, and `cvmx_bootmem_get_desc`.

## Control Flow
Initialization receives the bootloader-provided descriptor. Allocation scans the free-list for a range satisfying size, address bounds, alignment, and optional end-allocation behavior, then updates the descriptor and free block headers. Named allocation reserves a descriptor entry, prevents duplicate names, and optionally initializes a once-created block. Free is restricted mainly to named-block and initial free-list manipulation.

## State and Persistence Behavior
State is shared in physical memory: the descriptor, free-list headers embedded in free blocks, and named-block descriptors. Named blocks can persist across cooperating applications or kernel subsystems that know their names. The spinlock field protects concurrent access unless callers deliberately use `NO_LOCKING` under external locking.

## Dependencies and Integration Points
It integrates with `cvmx_bootinfo.phy_mem_desc_addr`, early Octeon memory setup, FPA pool allocation, command queue shared state, and other CVMX facilities that allocate named bootmem blocks. The ABI is shared with bootloader code and possibly 32-bit and 64-bit consumers.

## Risks
The structures are ABI-sensitive and referenced by bootloader assembly; changing layout or `CVMX_BOOTMEM_NAME_LEN` breaks compatibility. Freeing with the wrong physical address or size corrupts the free list. Misusing `NO_LOCKING` can race shared allocations. Alignment and address-bound handling must be precise because callers often need DMA-visible or hardware-constrained memory.

## Test Signals
Boot tests should verify descriptor version parsing, early allocations, named block reuse, range-restricted allocations, and lock behavior. Stress signals include repeated named alloc/free, allocation at exact addresses, high-address/end allocations, and no free-list corruption after failed allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu-defs.h

## Purpose
This header defines legacy Octeon CIU interrupt, watchdog, timer, reset, mailbox, QLM/JTAG, PCI, and BIST CSRs. It provides address builders and selected bitfield unions for core-local interrupt enables/status and platform control.

## Important APIs, Types, and Functions
`CVMX_CIU_ADDR()` is the base address builder. Macros cover per-core interrupt summaries/enables (`INTX_SUM0`, `INTX_EN0/1`, write-one set/clear variants, `EN2_PPX_IP4`, `SUM2_PPX_IP4`), global interrupt summary, timers, NMI, PCI INTA, reset/BIST/debug, QLM and JTAG controls, and soft reset/PCI reset controls. Inline address helpers `CVMX_CIU_MBOX_CLRX`, `CVMX_CIU_MBOX_SETX`, `CVMX_CIU_PP_POKEX`, and `CVMX_CIU_WDOGX` select family-specific addresses for CN68XX and later CIU layouts. Unions describe QLM tuning, QLM JTAG, soft PCI reset, timer, and watchdog fields.

## Control Flow
Most users compute a CSR address and read/write it. The inline helpers branch on `cvmx_get_octeon_family()` to handle families whose mailbox, poke, and watchdog registers moved. Interrupt code enables sources, reads summaries, acknowledges mailbox/timer/watchdog events, and routes them into MIPS interrupt lines.

## State and Persistence Behavior
CIU CSRs hold interrupt masks, pending summaries, watchdog counters/modes, timer lengths, reset state, and QLM control values. These are hardware persistent until reset or explicit writes. Watchdog and timer state changes can directly reset or interrupt cores.

## Dependencies and Integration Points
It depends on `asm/bitfield.h`, Octeon model/family helpers, and CSR address helpers. It integrates with MIPS interrupt setup, SMP mailbox IPIs, watchdog drivers, platform reset, PCI interrupt wiring, QLM configuration, and low-level board diagnostics.

## Risks
Family-specific address selection is high risk; the wrong CIU path can poke or watchdog the wrong register. Core IDs are masked, so sparse or multi-node numbering must be handled before using legacy CIU macros. Watchdog and reset fields can halt or reset hardware immediately. Interrupt write-one set/clear semantics must not be confused with normal read/modify/write.

## Test Signals
Signals include working timer interrupts, IPIs/mailboxes, watchdog poke/expiry behavior, PCI INTA delivery, reset paths, and no unexpected CIU BIST/debug errors across CN3xxx/CN6xxx/CN7xxx family builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu2-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu2-defs.h

## Purpose
This compact header defines CIU2 interrupt-controller CSR addresses for Octeon chips using the second-generation CIU layout. It focuses on per-core IP2/IP3 summary, source, enable, acknowledge, and write-one set/clear registers.

## Important APIs, Types, and Functions
Macros cover IP2 work queue, watchdog, and RML sources/enables; IP3 mailbox enable write-one clear/set; IP2/IP3 acknowledgements; raw work-queue status; per-core summaries; and `CVMX_CIU2_INTR_CIU_READY`. All address macros use `CVMX_ADD_IO_SEG()` and mask `block_id` or offset to 31 cores.

## Control Flow
There is no executable logic. Interrupt code selects a per-core CSR, reads summary/source/raw state, enables or disables bits through direct or W1S/W1C registers, and acknowledges delivered interrupts.

## State and Persistence Behavior
The CIU2 hardware keeps per-core pending, enable, and acknowledgement state. Enable bits persist until changed. Pending state reflects hardware interrupt sources and is cleared through the appropriate acknowledge or source-specific handling.

## Dependencies and Integration Points
It depends on Octeon CSR address mapping. It integrates with the Octeon IRQ driver, POW/work-queue interrupt delivery, watchdog interrupt handling, mailbox/IPI routing, and RML error/status interrupts.

## Risks
The register map is per-core and heavily offset-based; using the wrong `block_id` targets a different core. W1C/W1S register pairs must be used instead of unsafe read/modify/write under interrupt concurrency. The file provides addresses only, so callers must know the correct bit assignments from hardware context.

## Test Signals
Runtime signals include correct IP2/IP3 interrupt routing on CIU2 systems, mailbox IPI delivery, watchdog interrupt handling, work-queue interrupts, and clean enable/disable behavior with no stuck pending bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu2-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu3-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu3-defs.h

## Purpose
This header defines the CIU3 interrupt-controller register map used by newer Octeon platforms. It models interrupt source control, interrupt destination tables, per-destination pending interrupts, NMI, timers, ECC status, BIST, constants, and global stop/control registers.

## Important APIs, Types, and Functions
Address macros include global control/status (`FUSE`, `BIST`, `CONST`, `CTL`, `GSTOP`, `NMI`), destination registers (`DESTX_PP_INT`, `DESTX_IO_INT`), interrupt destination table entries (`IDTX_CTL`, `IDTX_IO`, `IDTX_PPX`), interrupt source controls (`ISCX_CTL`, `ISCX_W1C`, `ISCX_W1S`), summary interrupt enables (`SISCX`), timers (`TIMX`), ECC control/status, readiness, and slowdown. Unions expose fields for IDT size/destination counts, source enable/raw/IDT mapping, destination pending/new interrupt flags, PP and IO destination masks, ECC syndrome injection and SBE/DBE status, NMI masks, and timer length/one-shot mode.

## Control Flow
The file itself has no code. IRQ setup writes IDT mappings, points sources at IDT entries, enables sources, then interrupt handlers read destination pending registers and source status, clearing or setting bits through W1C/W1S CSRs as needed.

## State and Persistence Behavior
CIU3 hardware stores interrupt routing tables, source enable/raw state, per-destination pending state, timer state, ECC error status, and NMI masks. This state persists until changed or reset. ECC status can latch memory errors and must be cleared according to hardware semantics.

## Dependencies and Integration Points
It depends on Octeon CSR address helpers and endian bitfield layout. It integrates with the Octeon interrupt controller driver, SMP/NMI handling, per-core timers, IO interrupt routing, ECC reporting, and platform discovery through `CONST`.

## Risks
CIU3 exposes very large indexed spaces (`ISCX` up to 20-bit source indices), making off-by-one or wrong-source programming dangerous. IDT and destination fields are topology-sensitive; incorrect PP/IO masks can misroute or lose interrupts. ECC injection fields must be kept out of production paths. W1C/W1S use is mandatory for concurrent interrupt updates.

## Test Signals
Signals include correct IRQ routing to CPUs and IO destinations, functioning per-core timers, NMI delivery, source enable/disable tests, ECC status reporting/injection tests where safe, and no stuck `newint`/`intr` destination bits under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ciu3-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-cmd-queue.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-cmd-queue.h

## Purpose
This header provides the common Octeon command queue infrastructure used by hardware blocks such as PKO, ZIP, DFA, RAID, and DMA. It manages chained FPA-backed command buffers, shared queue state in bootmem, fair locking, and optimized inline command writes.

## Important APIs, Types, and Functions
`cvmx_cmd_queue_id_t` encodes unit and queue identifiers, with helpers for PKO and DMA queues. `cvmx_cmd_queue_result_t` reports success, no memory, full, invalid parameter, or already setup. `__cvmx_cmd_queue_state_t` packs queue state: ticket/serving, optional max depth, FPA pool, current buffer pointer, pool size, and current write index. `__cvmx_cmd_queue_all_state_t` stores ticket and state arrays.

Declared APIs initialize/shutdown queues, query length, and return the current command buffer. Inline helpers compute state index, lock/unlock with a ticket-style LL/SC loop, get state, and write one arbitrary command array or fixed two/three-word commands (`cvmx_cmd_queue_write`, `write2`, `write3`).

## Control Flow
Initialization allocates the first FPA command buffer and configures the owning hardware. Writers optionally acquire the queue lock, check max-depth if enabled, append command words to the current buffer when space remains, or allocate a new FPA buffer, link it from the old buffer's final word, advance `base_ptr_div128`, and continue writing. Unlock increments `now_serving` and issues `CVMX_SYNCWS`.

## State and Persistence Behavior
Queue state is global shared memory, typically a named bootmem block called `cvmx_cmd_queues`. Command buffers are FPA blocks linked by physical addresses. Queue state and pending command contents persist until the hardware consumes them or shutdown frees buffers back to FPA. Locks serialize multi-core software producers unless callers disable locking and provide external exclusion.

## Dependencies and Integration Points
It depends on FPA allocation/free, physical/virtual address conversion, Octeon assembly barriers, prefetching, compiler helpers, and hardware-specific wrappers that submit commands and ring doorbells. PKO layout is optimized for per-core/per-port queue locality.

## Risks
This is concurrency- and hardware-facing code. Incorrect index packing, buffer-size assumptions, or lock ordering can corrupt shared queues. FPA exhaustion returns `NO_MEMORY` mid-write before any new buffer can be linked. Disabling locking is only safe for carefully partitioned queues. The packed bitfields assume command buffers are 128-byte aligned and sizes fit the field widths.

## Test Signals
Stress multi-core command producers for PKO/DMA/ZIP users, including buffer-boundary writes, FPA exhaustion, max-depth enabled builds, queue shutdown after hardware stop, and lock fairness under contention. Packet transmission and DMA command completion are end-to-end signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-cmd-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-config.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-config.h

## Purpose
This header supplies default CVMX executive configuration values for Octeon networking and hardware helper code. It sizes FPA pools, reserves FAU and scratchpad regions, configures PKO queues, and selects packet-input helper behavior.

## Important APIs, Types, and Functions
Constants configure debug prints, null-pointer protection, LLM ports, PKO queues per interface/PCI/loop port, and helper max ports. FPA constants define pool sizes and assign packet, WQE, and output-buffer pools. FAU allocation macros and enums (`cvmx_fau_reg_64_t`, `32_t`, `16_t`, `8_t`) reserve aligned register ranges and define `CVMX_FAU_REG_AVAIL_BASE` and end. Scratchpad constants reserve `CVMX_SCR_SCRATCH`. Helper macros set first and chained packet skips, backpressure, IPD enable, POW tag type, input tag fields, skip mode, and forced RGMII backpressure disable.

## Control Flow
There is no runtime code. Other CVMX helpers include these macros at compile time to size pools, initialize IPD/PKO/FPA/FAU, and select packet tag/backpressure behavior. The linked FAU enum pattern ensures later register-size classes start at the previous class end.

## State and Persistence Behavior
The header defines compile-time configuration, not runtime state. Its values shape persistent hardware initialization such as FPA pool sizes, IPD buffer skips, input tag generation, and PKO queue layout.

## Dependencies and Integration Points
It references helper constants such as `CVMX_HELPER_PKO_MAX_PORTS_INTERFACE*`, `CVMX_CACHE_LINE_SIZE`, `CVMX_POW_TAG_TYPE_ORDERED`, and `CVMX_PIP_PORT_CFG_MODE_SKIPL2`. It integrates with FPA, FAU, IPD/PIP, PKO, POW, and Ethernet helper setup.

## Risks
Pool sizes and packet skip constants are data-path ABI choices; wrong values can break buffer alignment, DMA layout, or packet parsing. `CVMX_HELPER_ENABLE_IPD` is off by default, so callers must explicitly enable packet input after final configuration. FAU allocation enums currently reserve no counters; adding counters must preserve alignment and avoid exceeding 2048 bytes.

## Test Signals
Signals include successful packet I/O initialization, correct FPA pool block sizes, valid packet buffer headroom, expected POW tag fields, no FAU register overlap, and no packet drops from backpressure or IPD-enable sequencing mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-coremask.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-coremask.h

## Purpose
This header defines a bitmap type and minimal helpers for representing Octeon core sets, including sparse multi-node core numbering where node IDs create large gaps.

## Important APIs, Types, and Functions
`CVMX_MIPS_MAX_CORES` is 1024, `CVMX_COREMASK_ELTSZ` is 64, and `CVMX_COREMASK_BMPSZ` sizes the bitmap. `struct cvmx_coremask` contains `u64 coremask_bitmap[16]`. Inline helpers test a core bit (`cvmx_coremask_is_core_set`), copy masks (`cvmx_coremask_copy`), set the low 64 bits (`cvmx_coremask_set64`), and clear one core (`cvmx_coremask_clear_core`).

## Control Flow
Helpers compute word and bit indices from a core number and manipulate the bitmap. There is no iteration helper here; callers handle traversal or use the routines in boot and SMP setup.

## State and Persistence Behavior
The structure is plain in-memory state. It appears inside bootinfo as `ext_core_mask`, making its layout part of the bootloader ABI. Helper operations mutate only the supplied mask.

## Dependencies and Integration Points
It depends on kernel integer types, `bool`, and `memcpy` from included context. It integrates with `cvmx_bootinfo`, SMP core selection, multi-node initialization, and any role partitioning for shared Octeon binaries.

## Risks
The inline helpers do not bounds-check `core`; invalid or negative core numbers can index outside the bitmap. `cvmx_coremask_set64()` only initializes the low word, which is insufficient for CN78XX-style node 1+ core IDs. Callers must distinguish hardware CPUNum values from dense Linux CPU indices.

## Test Signals
Test sparse masks with core IDs 0-47, 128-175, and higher-node ranges. Verify bootinfo extended core masks select expected CPUs, invalid core IDs are filtered by callers, and low-64 compatibility paths still work on older systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-coremask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dbg-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dbg-defs.h

## Purpose
This header defines the Octeon `DBG_DATA` CSR and its chip-specific bit layouts. It is used to decode debug/fuse/clock-multiplier related data exposed through the debug register block.

## Important APIs, Types, and Functions
`CVMX_DBG_DATA` is the single CSR address. `union cvmx_dbg_data` provides the generic view (`data`, `dsel_ext`, `c_mul`) and chip-specific views for CN30XX (`pll_mul`), CN38XX (`d_mul`, `dclk_mul2`, `cclk_div2`), and CN58XX (`rem`). Each view is endian-aware through `__BIG_ENDIAN_BITFIELD`.

## Control Flow
There is no executable logic. Callers read `CVMX_DBG_DATA`, select the union member matching the detected chip, and decode multiplier or debug-data fields.

## State and Persistence Behavior
The register is hardware state. Reads are observational; this header does not write or persist software state. The decoded values usually represent reset-time or debug-selected hardware configuration.

## Dependencies and Integration Points
It depends on Octeon CSR address mapping and endian bitfield macros. It integrates with early clock-frequency derivation, diagnostics, chip identification, and low-level debug tooling.

## Risks
Selecting the wrong chip-specific view produces incorrect clock/debug interpretation. Because several fields are packed and reserved differently by model, generic code must not assume all multiplier fields exist. Endian layout mistakes can misread clock multipliers and lead to bad timing calculations.

## Test Signals
Validate clock and debug-data decoding on CN30XX, CN38XX, CN58XX, and generic paths. Compare derived clocks against bootloader-provided `eclock_hz`/`dclock_hz` or board documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dbg-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dpi-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dpi-defs.h

## Purpose
This header defines Octeon DPI DMA/PCIe interface CSRs. It covers DMA engine control, doorbells, instruction buffers, request banks, interrupt/error handling, SLI port configuration, per-port error capture, and DMA request accounting.

## Important APIs, Types, and Functions
Address macros include `CVMX_DPI_CTL`, `DMA_CONTROL`, `REQ_GBL_EN`, request error response/reset controls, packet error response, `INT_REG`/`INT_EN`, per-engine enable/buffer/count/doorbell/in-flight/next-address/request-bank registers, per-PP counts, NCB config, info and PINT info, SLI port config/error/info, and BIST. `CVMX_DPI_SLI_PRTX_ERR()` is an inline address helper with chip/pass-specific address selection. Unions describe enable/clock control, DMA counts and doorbells, instruction buffer start/size/idle, next address, request-bank state, DMA engine enable, error response status, interrupt summary/enables, PCIe MPS/MRRS/MOLR/QLM/halt config, and SLI error address/info.

## Control Flow
There is no driver logic in the file. DMA drivers program engine buffers and request controls, ring doorbells, poll or handle interrupts, and inspect error CSRs. The SLI error address helper switches by `cvmx_get_octeon_family()` and CN68XX pass to return the correct CSR address.

## State and Persistence Behavior
DPI CSRs hold DMA engine configuration, pending work counts, in-flight counts, doorbell state, error response policy, interrupt pending/enables, and PCIe port parameters. These persist in hardware until reset or reconfiguration; error registers may latch fault addresses and request metadata.

## Dependencies and Integration Points
It depends on Octeon model/family helpers and CSR address mapping. It integrates with DMA engine drivers, PCIe/SLI setup, interrupt handling, error reporting, and hardware command queues that feed DMA engines.

## Risks
Chip-specific SLI error offsets are easy to misselect, especially CN68XX pass 1 versus pass 2. Doorbell and count fields are hardware-synchronized; bad sequencing can lose DMA work or overrun instruction buffers. Error response/reset enable bits control whether faults are reported or reset, so overly broad writes can mask or amplify DMA failures.

## Test Signals
Exercise DMA transfers on every enabled engine, buffer-boundary and doorbell-count stress, PCIe error injection or fault reporting, SLI port config validation, interrupt enable/clear behavior, and family-specific tests for CN61XX/CN63XX/CN66XX/CN68XX/CNF71XX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dpi-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fau.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fau.h

## Purpose
This header provides inline APIs for Octeon's Fetch-and-Add Unit, a hardware atomic counter/register block. It supports synchronous fetch-add, tagwait fetch-add, asynchronous IOBDMA fetch-add into scratchpad, atomic add, and atomic write for 8/16/32/64-bit FAU registers.

## Important APIs, Types, and Functions
It defines the FAU I/O address bit fields, `cvmx_fau_op_size_t`, tagwait return structs for each width, and `cvmx_fau_async_tagwait_result_t`. Address builders `__cvmx_fau_store_address()`, `__cvmx_fau_atomic_address()`, and `__cvmx_fau_iobdma_data()` encode no-add/tagwait/register/size/value/scratch fields. Public inline APIs include `cvmx_fau_fetch_and_add*`, `cvmx_fau_tagwait_fetch_and_add*`, `cvmx_fau_async_fetch_and_add*`, `cvmx_fau_async_tagwait_fetch_and_add*`, `cvmx_fau_atomic_add*`, and `cvmx_fau_atomic_write*`.

## Control Flow
Synchronous fetch-add builds a special I/O load address and reads the old value with a width-specific helper. Smaller widths XOR the register address with endian swizzle constants. Tagwait forms set the tagwait bit and decode an error/value return. Async forms send an IOBDMA command to place the result in scratchpad. Atomic add/write forms write to a special I/O store address, using `noadd` to distinguish add from overwrite.

## State and Persistence Behavior
FAU register values are persistent hardware counters/registers until updated. Async operations write completion data to local scratchpad addresses supplied by the caller. The header itself keeps no software state.

## Dependencies and Integration Points
It depends on CVMX address builders, bit builders, I/O read/write helpers, scratchpad/IOBDMA send support, endian bitfield choices, and FAU register allocations from `cvmx-config.h`. It integrates with packet counters, synchronization primitives, POW/tag scheduling, and any fast shared counters in CVMX code.

## Risks
Only low bits of the add value are encoded for 32/64-bit operations, so large increments can truncate. Register alignment is width-specific and must match the typedef class. Async scratch addresses must be 8-byte aligned and reserved. Endian swizzling is required for sub-64-bit registers. Tagwait calls can return timeout/error and callers must inspect the error bit.

## Test Signals
Test 8/16/32/64-bit add and write operations, endian-correct subword registers, tagwait timeout handling, async scratchpad completion, counter wrap/truncation behavior, and concurrent multi-core increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fau.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa-defs.h

## Purpose
This header defines the CSR map and bitfield layouts for Octeon's Free Pool Allocator hardware. It covers pool sizes, marks, queue availability, page indices, pool start/end/thresholds, interrupts, BIST, address range errors, WART controls, and global FPA enable/reset state.

## Important APIs, Types, and Functions
Address macros include `CVMX_FPA_CTL_STATUS`, `BIST_STATUS`, `INT_ENB`, `INT_SUM`, per-pool `FPFX_MARKS/SIZE`, `QUEX_AVAILABLE`, `QUEX_PAGE_INDEX`, `POOLX_START_ADDR`, `POOLX_END_ADDR`, `POOLX_THRESHOLD`, packet/WQE thresholds, queue active/expected, address-range error, and `FPA_CLK_COUNT`. Unions expose global enable/reset/load/store behavior, memory error fields, FIFO read/write marks and sizes, queue available counts/page indices, pool threshold and address range fields, interrupt enable/summary bits for queue underflow/count-off/parity, pool threshold, free events, physical-address errors, and CN30XX/CN61XX/CN63XX/CN68XX-specific layouts including pool 8 support.

## Control Flow
No executable logic is present. FPA setup code writes pool start/end/threshold and FIFO mark/size CSRs, enables the allocator, then runtime allocation/free code uses FPA I/O addresses while diagnostics read availability and interrupt/error registers.

## State and Persistence Behavior
All state is in FPA hardware: pool ranges, free counts, FIFO marks, interrupt latches/enables, active/expected queue pointers, and global enable/reset bits. Counts change as blocks are allocated and freed. Error and threshold status persists until cleared according to hardware semantics.

## Dependencies and Integration Points
It depends on CSR address helpers and endian bitfield definitions. It is consumed by `cvmx-fpa.h`, FPA initialization/shutdown code, IPD/PKO packet buffer setup, command queue allocation, and interrupt/error reporting.

## Risks
FPA pool definitions are fundamental to packet and command-buffer memory safety. Wrong start/end/threshold values can allow out-of-range frees or allocator underflow. Interrupt unions have chip-specific variants; using the wrong view can miss pool8 or physical-address error bits. Some generated layouts contain duplicated-looking fields, so code should prefer known chip-specific definitions and avoid assuming reserved fields.

## Test Signals
Verify pool initialization, allocation/free counts, threshold interrupts, underflow/parity/count-off handling, pool range error reporting, pool 8 behavior on CN68XX-class hardware, and clean BIST status. Packet receive/transmit under memory pressure is an important integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa.h

## Purpose
This header provides the runtime API for Octeon's hardware Free Pool Allocator. It exposes pool metadata, enables the FPA, allocates blocks synchronously or asynchronously, frees blocks with or without ordering, and declares pool setup/shutdown helpers.

## Important APIs, Types, and Functions
Constants define 8 pools, 128-byte minimum block size, and 128-byte alignment. `cvmx_fpa_iobdma_data_t` describes async allocation command data. `cvmx_fpa_pool_info_t` records a pool's name, block size, base pointer, and starting element count, with global `cvmx_fpa_pool_info[]`. Inline helpers return pool name/base, test membership, enable FPA, allocate (`cvmx_fpa_alloc`), async allocate (`cvmx_fpa_async_alloc`), free without ordering (`cvmx_fpa_free_nosync`), and free with ordering (`cvmx_fpa_free`). External APIs include pool setup/shutdown and block-size query.

## Control Flow
`cvmx_fpa_enable()` reads status, warns if already enabled, applies pass1 FIFO mark workarounds with a short delay, then writes enable. Allocation reads from an FPA DID address and converts a physical address to a pointer. Async allocation sends an IOBDMA command to write the result to scratchpad. Free converts a pointer to physical, encodes the FPA pool DID into the address, optionally issues `CVMX_SYNCWS`, and writes the cache-line invalidate count to the FPA I/O address.

## State and Persistence Behavior
Pool metadata is software global state. Hardware pool contents and counts live in FPA CSRs/FIFOs and persist until blocks are allocated/freed or the unit is reset. Freeing transfers ownership of a memory block to hardware; callers must not touch it afterward without reallocation.

## Dependencies and Integration Points
It depends on Linux delay, CVMX address conversion and CSR helpers, `cvmx-fpa-defs.h`, Octeon model/pass detection, debug printing, barriers, and IOBDMA send support. It integrates with packet buffers, work queue entries, command queues, DMA descriptors, and bootmem-backed pool creation.

## Risks
Memory ordering is critical: `cvmx_fpa_free_nosync()` is unsafe for buffers modified by the core unless the caller supplied ordering elsewhere. Pool membership has no bounds checking for invalid pool IDs. Passing a bad pointer or wrong pool corrupts hardware free lists. Async scratch addresses must be aligned. Pass1 workaround programming must remain before enabling FPA on affected chips.

## Test Signals
Test pool setup, enable, sync and async allocation, ordered and unordered frees, membership checks, shutdown returning expected block counts, pass1 hardware workaround paths, and packet I/O under FPA pressure with no use-after-free buffer corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa.h -->
