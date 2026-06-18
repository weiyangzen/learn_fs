# Research: subset-b-001263

This grouped report covers the DMA40 and STM32 DMA source files requested for subset-b-001263. Each section is bounded by the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.c

## Purpose
`ste_dma40.c` is the main Linux DMAEngine provider for the ST-Ericsson DMA40 controller. It registers DMAEngine devices for logical slave channels, logical memcpy channels, and physical channels that can serve both slave and memcpy users. The driver discovers DMA40 hardware revision and channel counts, initializes register banks, manages event-line to physical-channel allocation, builds descriptors through the DMA40 low-level LLI helpers, handles DMA interrupts, and coordinates runtime/system power management.

## Important APIs, Types, And Functions
Key private types are `struct d40_base`, `struct d40_chan`, `struct d40_desc`, `struct d40_phy_res`, `struct d40_lcla_pool`, and `struct d40_gen_dmac`. `d40_base` is the per-controller state: MMIO base, revision, clocks, IRQ, DMAEngine devices, channel arrays, lookup tables, LCLA/LCPA memory, descriptor slab, interrupt scratch registers, PM backup buffers, and revision-specific register tables. `d40_chan` is the DMAEngine channel wrapper with lock-protected descriptor lists (`prepare_queue`, `pending_queue`, `queue`, `active`, `done`, `client`), physical-resource binding, default register configuration, runtime slave address state, and tasklet. `d40_desc` stores one DMA job, with physical or logical LLI arrays, current LLI progress, LCLA allocation count, DMAEngine tx descriptor, and cyclic flag.

Important entry points are `d40_probe`, `stedma40_init`, `d40_xlate`, `stedma40_filter`, `d40_alloc_chan_resources`, `d40_free_chan_resources`, `d40_prep_memcpy`, `d40_prep_slave_sg`, `dma40_prep_dma_cyclic`, `d40_issue_pending`, `d40_tx_status`, `d40_pause`, `d40_resume`, and `d40_terminate_all`. Internal control functions include `d40_allocate_channel`, `d40_free_dma`, `d40_config_write`, `d40_set_runtime_config_write`, `d40_queue_start`, `d40_desc_load`, `d40_log_lli_to_lcxa`, `dma_tc_handle`, `dma_tasklet`, and `d40_handle_interrupt`.

## Control Flow
Probe parses device tree platform data in `d40_of_probe`, detects hardware and revision-specific tables in `d40_hw_detect_init`, initializes physical-channel reservation state in `d40_phy_res_init`, maps LCPA SRAM, allocates or maps LCLA memory, requests the controller IRQ, enables runtime PM, registers DMAEngine devices, initializes hardware registers, and registers the OF DMA controller.

Channel acquisition flows through DMAEngine filtering. `d40_xlate` converts a device-tree DMA spec into `stedma40_chan_cfg` and calls `dma_request_channel`; `stedma40_filter` validates and stores the config. `d40_alloc_chan_resources` assigns cookies, defaults to memcpy config if no slave config exists, allocates a logical or physical channel with `d40_allocate_channel`, writes channel mode only when the physical resource was previously free, and sets priority/realtime event registers.

Descriptor preparation creates a `d40_desc`, computes the number of DMA40 LLI segments with `d40_sg_2_dmalen`, allocates LLI storage, writes logical or physical LLI arrays through `d40_prep_sg_log` or `d40_prep_sg_phy`, then places the descriptor on `prepare_queue`. Submit moves it to `pending_queue`; `issue_pending` splices pending descriptors to `queue` and starts the first idle descriptor. Completion IRQs are decoded through revision-specific interrupt lookup tables, acknowledge the bit, run `dma_tc_handle`, and schedule `dma_tasklet` to complete cookies and invoke callbacks outside the hard IRQ path.

## State And Persistence
Runtime state is mostly in memory: allocation bitmaps in `d40_phy_res`, active channel lookup tables, descriptor queues, LCLA allocation map, per-channel busy and pending counters, and runtime slave address/direction. Hardware-persistent state includes DMA40 global/channel registers, LCPA SRAM, LCLA memory, and event-line state. Runtime suspend saves global and channel parameter registers into `d40_base` backup arrays and restores them on resume; system suspend also handles the optional ESRAM regulator. No filesystem persistence is used.

## Dependencies And Integration Points
The driver depends on Linux DMAEngine, `dmaengine.h`, OF DMA registration, platform devices, AMBA PrimeCell IDs, clocks, runtime PM, regulators, IRQs, scatterlists, DMA mapping, slab caches, and the low-level helpers in `ste_dma40_ll.c/.h`. It integrates with device-tree clients through `#dma-cells` style args interpreted by `d40_xlate`, with clients through DMAEngine callbacks/cookies/residue, and with controller-specific SRAM via the `sram` phandle and optional `lcla_esram` resource.

## Risks
The highest risk areas are concurrency and hardware edge cases: shared physical resources between logical channels, event-line suspend/activate retries, dual list ownership between active/done/client queues, and runtime PM get/put pairing around busy channels. Descriptor allocation uses `GFP_NOWAIT`, so preparation can fail under memory pressure. LCLA allocation requires strict 18-bit alignment and falls back to a larger allocation; failures there prevent probe. Error IRQs are logged but do not appear to complete descriptors as failed, which may leave clients waiting after hardware errors. Several paths mutate `dma_cfg.dir` during runtime config, so clients relying on static direction assumptions need careful validation.

## Test Signals
Useful validation signals include successful probe with correct revision/channel count logs, `of_dma_controller_register` success, DMAEngine memcpy tests on logical and physical channels, slave SG transfers in both directions, cyclic audio-style transfers, pause/resume/terminate tests, residue correctness during active and paused transfers, runtime suspend/resume under idle and active workloads, and fault injection for invalid widths, burst mismatch, alignment failures, unavailable fixed channels, and LCLA allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.h

## Purpose
`ste_dma40.h` is the public local configuration contract for the DMA40 driver and its low-level helper code. It defines the channel mode model, DMA element and packet-size constants, maximum hardware limits, flow-control settings, and the `stedma40_chan_cfg` structure used by clients, OF translation, memcpy defaults, and LLI generation.

## Important APIs, Types, And Functions
The file exports no functions. Its important definitions are `STEDMA40_MAX_SEG_SIZE`, `STEDMA40_MAX_PHYS`, `STEDMA40_DEV_DST_MEMORY`, `STEDMA40_DEV_SRC_MEMORY`, `enum stedma40_mode`, `enum stedma40_mode_opt`, `enum stedma40_flow_ctrl`, `struct stedma40_half_channel_info`, and `struct stedma40_chan_cfg`. The half-channel info captures endianness, DMA bus width, packet size, and flow control. The full channel config adds transfer direction, high-priority/realtime flags, logical or physical mode, mode options, event/device type, source/destination half configs, and optional fixed physical-channel binding.

## Control Flow
There is no executable control flow in this header. The data defined here drives control flow in `ste_dma40.c` and `ste_dma40_ll.c`: channel filtering validates `mode`, `dir`, `dev_type`, and burst-width compatibility; allocation chooses logical or physical resources from `mode`; low-level register builders translate width, packet size, flow-control, endianness, and priority into DMA40 register fields.

## State And Persistence
The header defines the shape of in-memory configuration only. Instances of `stedma40_chan_cfg` are stored in each `d40_chan`, copied from device-tree filter data or default memcpy configs, and updated by runtime slave configuration. There is no persistent state or hardware access in this file.

## Dependencies And Integration Points
The structures use `enum dma_transfer_direction` and `enum dma_slave_buswidth` from the DMAEngine API, so this header is coupled to Linux DMAEngine types. It is included by both the main DMA40 provider and the low-level LLI builder, making it the shared semantic boundary between client-facing channel configuration and hardware-specific register encoding.

## Risks
The constants encode hardware-specific constraints that must match `ste_dma40_ll.h` register fields. A mismatch in packet-size constants between logical and physical modes would produce invalid LLIs. The `dev_type` field is overloaded for source or destination event selection depending on `dir`, which is compact but easy to misuse. The comment for `src_info` says it describes "Parameters for dst half channel" in one place, which is likely a typo and could confuse maintainers.

## Test Signals
Test coverage should verify that each supported `dma_slave_buswidth` and packet size maps correctly in low-level register output, that logical and physical memcpy defaults are accepted, that invalid mode/direction/device combinations fail in `d40_validate_conf`, and that fixed-channel and big-endian flags from OF specs survive into `d40_chan.dma_cfg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.c

## Purpose
`ste_dma40_ll.c` converts DMA40 channel configuration and scatterlists into hardware linked-list items for physical and logical DMA40 channels. It is the register-packing layer used by `ste_dma40.c` during descriptor preparation and LCPA/LCLA programming.

## Important APIs, Types, And Functions
Public helper functions are `d40_log_cfg`, `d40_phy_cfg`, `d40_phy_sg_to_lli`, `d40_log_sg_to_lli`, `d40_log_lli_lcpa_write`, and `d40_log_lli_lcla_write`. Private helpers include `d40_width_to_bits`, `d40_phy_fill_lli`, `d40_seg_size`, `d40_phy_buf_to_lli`, `d40_log_lli_link`, `d40_log_fill_lli`, and `d40_log_buf_to_lli`.

`d40_phy_cfg` and `d40_log_cfg` translate `stedma40_chan_cfg` into default source/destination config words. Physical config sets event line, master port, transfer mode, error/terminal interrupts, packet enable/size, element width, priority, and endianness. Logical config builds LCSP1/LCSP3 defaults with increment, master port, interrupt enable, packet size, and element width bits.

## Control Flow
Physical SG conversion starts with `d40_phy_sg_to_lli`. If no fixed target address is supplied, it enables address increment. Each SG entry is passed to `d40_phy_buf_to_lli`, which splits the buffer into legal hardware segment sizes using `d40_seg_size`. Each segment is packed by `d40_phy_fill_lli`, which validates address alignment and minimum transfer size, writes element count/index, pointer, config, and link pointer, and marks terminal interrupt only on the last required segment.

Logical SG conversion is similar but writes compact logical LCSP entries instead of physical standard channel registers. `d40_log_sg_to_lli` iterates the SG list, chooses either device address or SG address, and delegates splitting to `d40_log_buf_to_lli`. Later, the main driver uses `d40_log_lli_lcpa_write` for the first active item and `d40_log_lli_lcla_write` for linked entries; both call `d40_log_lli_link` to set source/destination next offsets and terminal interrupt bits.

## State And Persistence
The file does not maintain global state. It mutates caller-owned LLI arrays and writes logical LLIs to MMIO/SRAM-backed LCPA or LCLA memory with `writel_relaxed`. The generated LLIs persist only as long as the descriptor and associated DMA-visible memory remain valid.

## Dependencies And Integration Points
The code depends on DMAEngine width constants, Linux scatterlists, register bit definitions from `ste_dma40_ll.h`, and channel config types from `ste_dma40.h`. It is tightly integrated with `ste_dma40.c` descriptor allocation: physical LLIs are DMA-mapped and synchronized by the caller, while logical LLIs are copied into LCPA/LCLA windows during transfer loading.

## Risks
Alignment and size handling are critical. `d40_phy_fill_lli` rejects unaligned data and too-small transfers, while logical fill uses `BUG_ON` if a segment exceeds `STEDMA40_MAX_SEG_SIZE`, making upstream length calculation correctness important. Both physical and logical SG conversion assign the return value repeatedly; the caller checks only the last conversion result, so source-side failures could be overwritten by destination-side conversion if not handled carefully in callers. The segment sizing logic must maintain source and destination width compatibility or residue and element counts will be wrong.

## Test Signals
Tests should exercise width mappings for 1, 2, 4, and 8 byte widths; physical LLI generation for fixed device and incrementing memory addresses; logical LCSP address splitting; cyclic physical linkback; maximum segment splitting around `STEDMA40_MAX_SEG_SIZE`; unaligned SG rejection; terminal interrupt placement; and LCPA/LCLA writes with expected next offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.h

## Purpose
`ste_dma40_ll.h` is the DMA40 low-level hardware definition header. It defines DMA40 register offsets, bit positions and masks for physical and logical standard channel parameters, LCPA/LCLA memory layout structures, physical and logical LLI structures, and prototypes for the LLI/register packing helpers implemented in `ste_dma40_ll.c`.

## Important APIs, Types, And Functions
Key definitions include global DMA register offsets such as `D40_DREG_GCC`, interrupt status/clear registers, logical channel status/clear registers, revision-specific extended registers, PrimeCell ID offsets, and per-channel standard register offsets (`D40_CHAN_REG_SSCFG`, `D40_CHAN_REG_SSELT`, `D40_CHAN_REG_SSPTR`, `D40_CHAN_REG_SSLNK`, destination equivalents). It also defines event grouping macros such as `D40_TYPE_TO_GROUP`, `D40_TYPE_TO_EVENT`, and `D40_PHYS_TO_GROUP`.

Important hardware-mapped structures are `struct d40_phy_lli`, `struct d40_phy_lli_bidir`, `struct d40_log_lli`, `struct d40_log_lli_bidir`, `struct d40_log_lli_full`, and `struct d40_def_lcsp`. `enum d40_lli_flags` defines address-increment, terminal-interrupt, cyclic, and last-link controls. Function prototypes expose physical/logical config and SG-to-LLI conversion plus LCPA/LCLA write helpers.

## Control Flow
There is no executable control flow. The macros directly shape control flow in the main driver: interrupt tables select registers from this header, allocation maps event groups and lines using its macros, channel command code reads/writes active and link registers using its offsets, and LLI writers use the bit masks to set next-link and element-count fields.

## State And Persistence
The header describes hardware and DMA-visible memory layouts. The structures are intentionally minimal and aligned because hardware reads them directly. State exists when instances are allocated by the main driver as descriptor LLIs or mapped to LCPA/LCLA memory; this header itself stores no state.

## Dependencies And Integration Points
It depends on `ste_dma40.h` through function prototypes using `stedma40_chan_cfg` and `stedma40_half_channel_info`, and on Linux scatterlist/DMA address types through prototypes. It is the integration point between C structures and DMA40 silicon register layout; changes here can affect probe initialization, interrupt handling, descriptor loading, power-management backup, and event-line control.

## Risks
Most constants are hardware contract values, so off-by-one or wrong mask changes are severe. The same bit positions are reused with different meanings in physical and logical modes, which increases maintenance risk. The logical `d40_log_lli` and full LCPA structures must remain exactly hardware-shaped; adding fields or changing alignment would corrupt DMA-visible layout. The many revision-specific register blocks require careful pairing with revision selection in `ste_dma40.c`.

## Test Signals
Validation should include compile-time structure-size/alignment expectations, register write/read traces from probe and descriptor load, interrupt status decoding on v4a and v4b tables, LCPA/LCLA layout checks, and hardware or emulated DMA tests that verify event group mapping and link traversal for physical and logical channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/Kconfig

## Purpose
This Kconfig file exposes build-time configuration symbols for STM32 DMA controller drivers when `ARCH_STM32` or `COMPILE_TEST` is enabled. It controls inclusion of the classic STM32 DMA controller, STM32 DMAMUX router, STM32 MDMA controller, and STM32 DMA3 controller.

## Important APIs, Types, And Functions
The configuration symbols are `STM32_DMA`, `STM32_DMAMUX`, `STM32_MDMA`, and `STM32_DMA3`. `STM32_DMA`, `STM32_MDMA`, and `STM32_DMA3` select `DMA_ENGINE`; all except DMAMUX also select or rely on `DMA_VIRTUAL_CHANNELS`. `STM32_DMAMUX` depends on `STM32_DMA`, reflecting that the router is useful only with the classic STM32 DMA master in this directory. `STM32_MDMA` depends on `OF`. `STM32_DMA3` is tristate while the others are bool in this file.

## Control Flow
There is no runtime control flow. The build system evaluates the symbols and feeds the Makefile object selections. The top-level condition hides these options outside STM32 builds unless compile-testing is enabled.

## State And Persistence
Configuration state is stored in the kernel `.config` and influences compiled objects. There is no runtime state in this file.

## Dependencies And Integration Points
The file integrates with the kernel Kconfig system, the DMAEngine framework through selected symbols, and `drivers/dma/stm32/Makefile` through matching `CONFIG_STM32_*` object rules. It also controls whether device-tree compatible platform drivers for STM32 DMA variants can be built into or loaded by the kernel.

## Risks
Because `STM32_DMAMUX` depends specifically on `STM32_DMA`, configurations using DMA3 with a different routing model are not enabled by this symbol. The mix of bool and tristate options means DMA3 can be modular while classic STM32 DMA cannot from this Kconfig context. Missing dependency updates can surface as compile-test failures when headers or framework APIs change.

## Test Signals
Useful signals are `olddefconfig` coverage for STM32 and COMPILE_TEST builds, build tests for each symbol enabled independently where dependencies allow, and module/built-in link checks confirming that Makefile object selection matches the Kconfig symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/Makefile

## Purpose
The STM32 DMA Makefile maps Kconfig symbols to object files for the STM32 DMA family drivers in this directory.

## Important APIs, Types, And Functions
The object rules are `obj-$(CONFIG_STM32_DMA) += stm32-dma.o`, `obj-$(CONFIG_STM32_DMAMUX) += stm32-dmamux.o`, `obj-$(CONFIG_STM32_MDMA) += stm32-mdma.o`, and `obj-$(CONFIG_STM32_DMA3) += stm32-dma3.o`. There are no functions or types.

## Control Flow
Kernel kbuild expands each `obj-$()` rule based on the resolved `.config`. Built-in symbols compile into the kernel image, tristate module values compile as modules when allowed by the corresponding Kconfig type, and disabled symbols omit the objects.

## State And Persistence
The Makefile has no runtime state. Its effect persists only through generated build artifacts.

## Dependencies And Integration Points
It integrates directly with `stm32/Kconfig` and the kernel build system. The object names correspond to platform drivers that register with DMAEngine and OF DMA routing at runtime.

## Risks
The main risk is drift between Kconfig symbols and object names. If a source file is renamed or a Kconfig symbol changes without updating this Makefile, the driver silently stops building for that configuration. Because `stm32-mdma.o` is listed but not part of this research subset, changes to Kconfig around MDMA should still consider that object.

## Test Signals
Build tests with each `CONFIG_STM32_*` symbol enabled should show the expected object compilation. `make drivers/dma/stm32/` under COMPILE_TEST is the direct smoke signal, with module installation checks for `STM32_DMA3=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma.c

## Purpose
`stm32-dma.c` is the DMAEngine driver for the classic STM32 DMA controller. It supports slave SG transfers, cyclic transfers, optional memory-to-memory transfers, pause/resume, residue reporting, runtime PM clock control, and optional interaction with STM32 MDMA through peripheral config.

## Important APIs, Types, And Functions
Important types are `struct stm32_dma_device`, `struct stm32_dma_chan`, `struct stm32_dma_desc`, `struct stm32_dma_sg_req`, `struct stm32_dma_chan_reg`, `struct stm32_dma_cfg`, and `struct stm32_dma_mdma_config`. The descriptor is a flexible array of per-SG register snapshots. Each channel keeps a `virt_dma_chan`, current descriptor, next SG index, DMA slave config, cached register config, FIFO threshold, memory width/burst, status, and MDMA trigger metadata.

DMAEngine operations are implemented by `stm32_dma_alloc_chan_resources`, `stm32_dma_free_chan_resources`, `stm32_dma_tx_status`, `stm32_dma_issue_pending`, `stm32_dma_prep_slave_sg`, `stm32_dma_prep_dma_cyclic`, `stm32_dma_prep_dma_memcpy`, `stm32_dma_slave_config`, `stm32_dma_pause`, `stm32_dma_resume`, `stm32_dma_terminate_all`, and `stm32_dma_synchronize`. Platform integration is through `stm32_dma_probe`, `stm32_dma_of_xlate`, and the `st,stm32-dma` match table.

## Control Flow
Probe maps registers, enables the clock, optionally resets hardware, configures DMAEngine capabilities, initializes eight virtual channels, registers the DMA device, requests per-channel IRQs, registers the OF DMA controller, and enables runtime PM. OF translation expects four cells: channel id, request line, stream config, and feature flags. It reserves a slave channel and calls `stm32_dma_set_config`, which seeds stream register bits, request line, interrupts, FIFO threshold/direct mode, alternate acknowledge, and MDMA stream id.

Transfer preparation validates channel configuration and builds a software descriptor. `stm32_dma_set_xfer_param` computes data widths, burst sizes, FIFO/direct mode, direction bits, peripheral address, and register fields. Slave SG and cyclic prep fill one register snapshot per SG or period; memcpy prep splits large copies into aligned chunks. `issue_pending` pulls the next virtual descriptor, programs SCR/SPAR/SM0AR/SM1AR/SFCR/SNDTR, clears pending IRQs, and enables the stream.

The IRQ handler decodes FIFO, direct mode, transfer complete, half-transfer, and error flags. Transfer complete advances cyclic callbacks or completes non-cyclic descriptors, then starts queued work. Pause disables the stream and snapshots NDTR/address-relevant register state. Resume adjusts peripheral/memory addresses by the consumed offset and re-enables the stream; cyclic double-buffer mode has special reconfiguration paths.

## State And Persistence
Runtime state is per-channel in memory and hardware registers. Descriptors store immutable register snapshots for each segment. `chan->desc`, `next_sg`, `busy`, and `status` are protected by the virt-dma lock. Runtime PM only gates the clock; this driver does not save and restore active channel registers across runtime suspend because resources are held while channels are allocated and system suspend refuses if streams are enabled.

## Dependencies And Integration Points
The driver depends on DMAEngine, `virt-dma`, OF DMA, platform resources, clocks, reset controls, runtime PM, scatterlists, DMA mapping, bitfield helpers, and iopoll. It integrates with STM32 device-tree clients via DMA spec cells and with STM32 MDMA by filling `stm32_dma_mdma_config` in `dma_slave_config.peripheral_config` when requested.

## Risks
Pause/resume and cyclic double-buffer handling are the most complex paths, especially address offset correction after NDTR changes and CT/DBM toggling. FIFO threshold and burst selection must avoid configurations that leave bytes stuck in FIFO. The IRQ handler logs some errors but does not always complete descriptors as failed. The residue computation explicitly handles races where hardware swaps double buffers around the NDTR read; this is an important but fragile approximation. Probe requests exactly eight IRQs matching `STM32_DMA_MAX_CHANNELS`, so device-tree IRQ layout must be correct.

## Test Signals
Signals include successful `st,stm32-dma` probe, DMAEngine dmatest memcpy when `st,mem2mem` is set, slave RX/TX SG tests with 1/2/4 byte widths, cyclic audio periods with one and multiple periods, pause/resume during cyclic and SG transfers, residue under active double-buffer mode, MDMA-triggered transfers, runtime suspend/resume while idle, and system suspend refusal while a stream is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma3.c -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma3.c

## Purpose
`stm32-dma3.c` is the DMAEngine provider for the newer STM32 DMA3 controller, currently matched for `st,stm32mp25-dma3`. It supports DMA slave, private channels, cyclic transfers, memcpy, hardware linked lists, channel security/CID filtering, semaphore-controlled channels, residue/in-flight reporting, runtime PM, and system suspend safety checks.

## Important APIs, Types, And Functions
Key types are `struct stm32_dma3_ddata`, `struct stm32_dma3_chan`, `struct stm32_dma3_swdesc`, `struct stm32_dma3_lli`, `struct stm32_dma3_hwdesc`, and `struct stm32_dma3_dt_conf`. A software descriptor owns a flexible array of DMA-pool-backed hardware descriptors. A channel stores virtual DMA state, hardware id/IRQ, FIFO size, max burst, semaphore state, DT config, DMA slave config, current software descriptor, transfer-complete event mode, and DMA status.

Important functions include descriptor allocation/free (`stm32_dma3_chan_desc_alloc`, `stm32_dma3_chan_desc_free`), hardware descriptor construction (`stm32_dma3_chan_prep_hw`, `stm32_dma3_chan_prep_hwdesc`), start/stop/suspend/reset (`stm32_dma3_chan_start`, `stm32_dma3_chan_stop`, `stm32_dma3_chan_suspend`, `stm32_dma3_chan_reset`), preparation APIs (`stm32_dma3_prep_dma_memcpy`, `stm32_dma3_prep_slave_sg`, `stm32_dma3_prep_dma_cyclic`), status/residue (`stm32_dma3_tx_status`, `stm32_dma3_chan_set_residue`), channel filtering/OF translation (`stm32_dma3_filter_fn`, `stm32_dma3_of_xlate`), RIF/CID validation (`stm32_dma3_check_rif`), and probe/PM functions.

## Control Flow
Probe maps registers, enables the clock, resets hardware, initializes DMAEngine capabilities, reads hardware channel/request/master-port/FIFO configuration, applies platform AXI burst limits, allocates channel state, reserves secure or inaccessible channels through `stm32_dma3_check_rif`, registers the DMAEngine device and individual channels, requests per-channel IRQs, registers the OF DMA controller, and enables runtime PM.

OF translation receives request line, channel config, and transfer config. It filters generic DMA channels by optional `dma-channel-mask`, semaphore availability, and FIFO-size match, then stores the DT config. Resource allocation resumes the device, creates a DMA pool for aligned hardware descriptors, and takes the channel semaphore when required.

Preparation computes how many linked-list items are needed, allocates DMA-visible descriptors, computes CTR1/CTR2/CCR fields for direction, widths, ports, bursts, packing/unpacking, request mode, and transfer-complete event mode, then links descriptors either linearly or cyclically. `issue_pending` starts the first queued descriptor by writing the first hardware descriptor to channel registers and enabling `CCR_EN`. IRQs check the masked interrupt status, complete or callback cyclic transfers on TCF, reset and mark error on user setting, update link, or data transfer errors, and clear status flags.

## State And Persistence
State lives in `stm32_dma3_ddata`, per-channel structures, DMA-pool descriptor memory, channel registers, and optional hardware semaphores. Runtime suspend only disables the clock. System suspend refuses if any registered channel has `CCR_EN` set. Resume reacquires semaphores for channels that had them before low power, because register reset can drop semaphore state.

## Dependencies And Integration Points
The driver depends on DMAEngine, `virt-dma`, OF DMA, platform resources, clocks, optional reset controls, DMA pools, runtime PM, bitfield helpers, and iopoll. It integrates with STM32 resource isolation/CID hardware through SECCFGR/CCIDCFGR/CSEMCR, with device-tree clients through three DMA spec cells, and with dmatest/memcpy users through DMA_MEMCPY support.

## Risks
Hardware linked-list addressing is limited by `CLLR_LA` and 32-byte descriptor alignment; oversized descriptor counts must be rejected. Residue requires temporarily suspending an active channel and reasoning about FIFO bytes, pack/unpack mode, and current linked-list pointer, so races and timeout handling are significant. Security/CID handling can deny channels depending on boot firmware configuration. Semaphore state can be lost during low power and must be reacquired. User-setting errors indicate invalid prepared register combinations and trigger reset, so width, port, burst, and packing decisions are high-risk.

## Test Signals
Useful signals include successful probe with revision log, channel availability under secure/CID configurations, DMAEngine memcpy across multiple block sizes including block-limit boundaries, slave SG with refactored and non-refactored linked lists, cyclic callbacks, residue and in-flight bytes during pack/unpack transfers, semaphore allocation/free and suspend/resume reacquisition, system suspend refusal for enabled channels, and IRQ-path tests for TCF, USEF, ULEF, and DTEF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dmamux.c

## Purpose
`stm32-dmamux.c` is a DMA router driver for STM32 DMAMUX hardware. It allocates DMAMUX output channels, programs request routing registers, rewrites DMA specifier arguments so requests are forwarded to an underlying STM32 DMA master, and saves/restores routing state across system sleep.

## Important APIs, Types, And Functions
Important types are `struct stm32_dmamux` and `struct stm32_dmamux_data`. The route object stores selected DMA master, input request, and mux channel id. The device data contains a `dma_router`, clock, MMIO base, request counts, spinlock, in-use bitmap, CCR backup array, and per-master DMA request counts.

Key functions are `stm32_dmamux_probe`, `stm32_dmamux_route_allocate`, `stm32_dmamux_free`, `stm32_dmamux_runtime_suspend`, `stm32_dmamux_runtime_resume`, `stm32_dmamux_suspend`, and `stm32_dmamux_resume`. `stm32_dmamux_init` registers the platform driver at `arch_initcall`, before many client drivers request DMA channels.

## Control Flow
Probe validates the DMAMUX node and `dma-masters` property, allocates flexible device data sized for all masters, checks that each master is compatible with `st,stm32-dma`, reads each master's `dma-requests` count, bounds the total by `STM32_DMAMUX_MAX_DMA_REQUESTS`, reads the mux input request count, maps registers, enables the clock, optionally resets when multiple masters exist, clears all DMAMUX channel control registers, enables runtime PM, and registers an OF DMA router.

Route allocation validates three DMAMUX args, finds a free mux output bit under lock, determines which master owns that output range, obtains the master phandle, resumes the DMAMUX device, records the input request, rewrites `dma_spec` into the selected master format, writes the mux request into `STM32_DMAMUX_CCR(chan_id)`, and returns route data. Freeing the route clears the CCR, releases the in-use bit, runtime-PM puts the device, and frees the route object.

## State And Persistence
Runtime state is the `dma_inuse` bitmap, programmed CCR registers, and route objects owned by DMA router clients. System suspend stores each CCR in `ccr[]` after resuming the device and restores them on resume. Runtime suspend only disables the clock. There is no filesystem persistence.

## Dependencies And Integration Points
The driver depends on OF DMA router support, platform devices, clocks, optional reset controls, runtime PM, spinlocks, and the underlying STM32 DMA master driver. It integrates with device tree through `st,stm32h7-dmamux`, `dma-masters`, `dma-requests`, and routed DMA specifier rewriting. Its output is consumed by `of_dma_router_xlate`, which later calls the selected master DMA controller.

## Risks
The route allocator checks `dma_spec->args[0] > dmamux_requests`; if request numbers are zero-based, the exact upper-bound semantics should match bindings. The in-use bit is set before master phandle and runtime PM success, so all error paths must clear it, which this code attempts. The code assumes master nodes are classic `st,stm32-dma`; adding DMA3 or other masters requires match updates and argument rewrite changes. CCR backup uses a fixed maximum array sized for 32 outputs, so `dma_requests` must remain bounded.

## Test Signals
Signals include probe with one and multiple DMA masters, route allocation until exhaustion, correct DMA spec rewrite for each master range, CCR programming and clearing on route free, runtime PM get/put balance during active routes, suspend/resume preserving CCR mappings, and error-path tests for bad arg count, invalid request, unsupported master, missing phandle, and clock/reset failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dmamux.c -->
