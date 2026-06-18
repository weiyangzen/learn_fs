# Research: subset-b-004341

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-common.h

## Purpose

`xgbe-common.h` is the shared register map and bitfield access contract for the AMD XGBE Ethernet driver. It names the Synopsys XGMAC DMA, MAC, MMC, MTL, PCS, SerDes, MAC-control, I2C, descriptor, and MDIO fields used by the implementation files in this directory. The file contains no executable functions, but it is the central ABI between C code and the device's memory-mapped and MDIO-visible hardware blocks.

The header is intentionally source-tree-aligned with the rest of the xgbe driver: `xgbe-dev.c`, `xgbe-drv.c`, `xgbe-desc.c`, `xgbe-debugfs.c`, DCB, PHY, I2C, PTP, and platform/PCI code all depend on these offsets and helper macros to avoid open-coded shifts and register arithmetic.

## Important APIs, Types, and Macros

- DMA global registers: `DMA_MR`, `DMA_SBMR`, `DMA_ISR`, AXI cache registers, descriptor prefetch registers, and channel register blocks starting at `DMA_CH_BASE` with `DMA_CH_INC`.
- MAC registers: transmit/receive control, packet filter, VLAN, flow control, queue mapping, hardware feature registers, MDIO, GPIO, MAC address filters, RSS, timestamp/PPS registers, and interrupt fields.
- MMC counters: transmit and receive counter offsets plus interrupt-enable/status bitfield definitions.
- MTL registers: queue operation mode, queue FIFO sizes, flow-control thresholds, traffic class ETS registers, queue-to-TC mapping, and dynamic queue/channel mapping.
- PCS, SerDes, RxTx, MAC-control, and I2C register definitions: these support XPCS windowed access, SerDes workarounds, platform properties, ECC status, and internal I2C transactions.
- Descriptor and packet bit definitions: `RX_PACKET_ATTRIBUTES`, `RX_PACKET_ERRORS`, `RX_NORMAL_DESC*`, `RX_CONTEXT_DESC*`, `TX_PACKET_ATTRIBUTES`, `TX_CONTEXT_DESC*`, and `TX_NORMAL_DESC*`.
- MDIO/vendor definitions: conditional definitions for PMA/PCS/AN/vendor MMD registers, clause 37/73 masks, KR training bits, CDR tracking, PMA reset/signal/valid/adaptation bits, and PLL control.
- Bitfield helpers: `GET_BITS`, `SET_BITS`, little-endian variants, and wrapper macros such as `XGMAC_GET_BITS`, `XGMAC_SET_BITS_LE`, `XP_GET_BITS`, and `XI2C_SET_BITS`.
- Register access helpers: `XGMAC_IOREAD/IOWRITE`, `XGMAC_MTL_IOREAD/IOWRITE`, `XGMAC_DMA_IOREAD/IOWRITE`, `XPCS{16,32}_IOREAD/IOWRITE`, `XSIR*`, `XRXTX`, `XP`, `XI2C`, and MDIO helpers `XMDIO_READ`, `XMDIO_WRITE`, and masked variants.

## Control Flow and Register Semantics

The file enables a consistent three-step pattern throughout the driver: read a register or descriptor word, extract or modify a named field, then write the value back. For queue/channel-specific hardware blocks, the macros compute offsets from a base plus an index stride, which is how `xgbe-dev.c` configures every DMA channel, MTL queue, and traffic class without duplicating address arithmetic.

Descriptor helpers operate on little-endian descriptor fields because DMA descriptors are shared with hardware. Normal host registers use CPU-endian MMIO values. This distinction is visible in transmit and receive paths: `xgbe-dev.c` writes TX/RX descriptors with `XGMAC_SET_BITS_LE`, while configuration paths write device registers with `XGMAC_IOWRITE_BITS`.

The MDIO helpers are built on `pdata->hw_if.read_mmd_regs` and `write_mmd_regs`, so code using `XMDIO_*` is abstracted from the platform-specific XPCS windowing implementation. The helpers inject `XGBE_ADDR_C45` and encode MMD/register address fields into the expected hardware access format.

## State and Persistence Behavior

This header does not own runtime state. Its macros mutate the state pointed to by `struct xgbe_prv_data`, `struct xgbe_channel`, hardware descriptor memory, or local variables passed by the caller. Persistence is therefore entirely hardware-side or caller-side: register writes survive until reset/power management reconfiguration, descriptor writes persist in DMA-coherent memory until the ring is reinitialized, and bitfield manipulations on local values persist only if the caller writes them back.

## Dependencies and Integration Points

`xgbe-common.h` depends on standard kernel primitives such as `BIT()`, endian conversion helpers, `ioread32/iowrite32`, `ioread16/iowrite16`, and the surrounding xgbe private structures declared in `xgbe.h`. It is included by files that implement the netdev path, descriptor allocator, DCB operations, debugfs register access, PHY/PCS access, I2C, and PTP support. Because it names hardware registers directly, changes here must be evaluated against all driver call sites and the relevant hardware programming manual.

## Risks and Failure Modes

- Incorrect bit index or width definitions can silently program the wrong hardware field, causing data-path hangs, wrong offload behavior, or link failures.
- `SET_BITS` uses `0x1 << width`; definitions with widths at or above the native literal width would be unsafe, so field widths must remain within expected register bit ranges.
- Read-modify-write helpers are not inherently synchronized. Callers must hold the appropriate lock or be in a serialized context when registers can be touched concurrently, especially XPCS window selection and RSS programming.
- The little-endian descriptor helpers must be used only for descriptor words. Mixing descriptor and MMIO helpers would corrupt byte ordering.
- Debugfs uses these macros for raw register access, so malformed offsets selected by users can touch arbitrary mapped registers if higher layers do not constrain them.

## Test Signals

Useful validation includes building the driver with sparse/endian warnings enabled, exercising netdev open/close, TX/RX traffic, VLAN filtering/stripping, RSS, VXLAN, DCB/PFC, PTP timestamping, MDIO/PHY access, and debugfs register reads. Hardware feature decoding in `xgbe_get_all_hw_features()` is a broad smoke test for MAC feature fields. Descriptor-level tests should verify that DMA ownership transitions, checksum/TSON/VLAN/VXLAN bits, and RX status parsing match expected packets under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dcb.c

## Purpose

`xgbe-dcb.c` connects the AMD XGBE driver to Linux DCBNL for IEEE 802.1Qaz Enhanced Transmission Selection and Priority Flow Control. It validates user-provided ETS/PFC policy, stores accepted policy in `struct xgbe_prv_data`, and calls hardware-interface hooks implemented in `xgbe-dev.c` to reprogram traffic classes, queue mapping, FIFO allocation, and pause behavior.

The file is deliberately small and policy-oriented. It does not write registers directly; it translates DCBNL operations into driver state changes and delegates hardware programming to `pdata->hw_if`.

## Important APIs and Functions

- `xgbe_dcb_ieee_getets()` reports `ets_cap` from `pdata->hw_feat.tc_cnt` and returns the saved `struct ieee_ets` fields when configured.
- `xgbe_dcb_ieee_setets()` validates traffic class mappings and TSA algorithms, enforces ETS bandwidth totals, saves the requested ETS policy, updates `pdata->num_tcs`, and invokes `config_dcb_tc`.
- `xgbe_dcb_ieee_getpfc()` reports PFC class capability and returns saved PFC enable, MBC, and delay values.
- `xgbe_dcb_ieee_setpfc()` validates the PFC enable mask against supported traffic classes, saves the policy, and invokes `config_dcb_pfc`.
- `xgbe_dcb_getdcbx()` advertises host-managed IEEE DCBX.
- `xgbe_dcb_setdcbx()` rejects unsupported or incomplete DCBX modes; the driver only accepts `DCB_CAP_DCBX_HOST | DCB_CAP_DCBX_VER_IEEE`.
- `xgbe_dcbnl_ops` is the exported `struct dcbnl_rtnl_ops` table, returned by `xgbe_get_dcbnl_ops()`.

## Control Flow

ETS set begins by walking all eight IEEE priority/traffic-class slots. It logs TX/RX bandwidth and TSA values, computes the maximum requested traffic class from both priority mappings and explicit TC settings, and accepts only strict priority and ETS algorithms. If any TC uses ETS, all ETS `tc_tx_bw[]` values must sum to 100. The accepted config is copied into a devm-managed `pdata->ets` allocation, `pdata->num_tcs` is set to the highest used TC plus one, and the hardware is reconfigured.

PFC set logs the requested capability, enable mask, MBC, and delay; then it rejects bits outside the hardware TC count. Accepted data is copied into devm-managed `pdata->pfc`, after which `config_dcb_pfc` recomputes lossless FIFO thresholds and flow-control bits.

## State and Persistence Behavior

The file persists DCB policy in `pdata->ets`, `pdata->pfc`, and `pdata->num_tcs`. Allocations use `devm_kzalloc(pdata->dev, ...)`, so memory lifetime is tied to the device, not to each DCB operation. Hardware state is volatile and is re-applied through `xgbe-dev.c` paths during device initialization or when DCB setters run. No on-disk or firmware persistence is performed.

## Dependencies and Integration Points

The file depends on Linux `netdevice.h`, `net/dcbnl.h`, IEEE 802.1Qaz structures, and the xgbe private data and hardware-interface callbacks. It integrates with:

- DCBNL user interfaces such as `dcb`/`lldpad`.
- `xgbe-dev.c` functions `xgbe_config_dcb_tc()` and `xgbe_config_dcb_pfc()`.
- netdev traffic class APIs via the delegated `config_tc` path.
- PFC queue and FIFO threshold calculations used by the receive flow-control code.

## Risks and Failure Modes

- The file assumes `pdata->hw_feat.tc_cnt` is already populated correctly. Bad feature decoding can reject valid DCB policy or accept unsupported classes.
- ETS bandwidth validation sums all TC weights marked ETS; callers must set strict classes with zero or ignored bandwidth as appropriate.
- `pdata->num_tcs = max_tc + 1` means sparse TC selections still expose all classes up to the maximum.
- DCB updates can reconfigure live data-path behavior through callbacks. The delegated PFC path stops TX queues and suspends RX when needed, but race coverage depends on those lower-level paths.
- There is no semantic validation of PFC delay beyond storing the value; hardware feasibility is handled later by FIFO and threshold calculations.

## Test Signals

Test with `dcb` or equivalent DCBNL tooling: valid strict-only ETS, valid ETS weights summing to 100, invalid TSA values, over-capacity TC mappings, invalid PFC masks, and live PFC toggles under traffic. Inspect `tc -s qdisc`, netdev traffic class mappings, pause/PFC counters, and driver logs. Regression signals include failed `config_dcb_tc`, FIFO allocation warnings in `xgbe-dev.c`, dropped traffic during live PFC changes, or wrong queue selection for VLAN priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-debugfs.c

## Purpose

`xgbe-debugfs.c` exposes low-level debugging controls for AMD XGBE hardware registers. It creates one debugfs directory per netdev and provides register selector/value pairs for XGMAC MMIO, XPCS MDIO/MMD access, optional MAC property registers, optional I2C control registers, and optional auto-negotiation CDR workaround booleans.

This is a diagnostic surface rather than a data-path component. It gives privileged users raw read/write access to selected register spaces using the same register helper macros as the driver.

## Important APIs and Functions

- `xgbe_common_read()` formats a 32-bit value as `0x%08x\n` and uses `simple_read_from_buffer`.
- `xgbe_common_write()` accepts one hexadecimal integer at offset zero and stores it in a caller-provided `unsigned int`.
- XGMAC files: `xgmac_register` selects `pdata->debugfs_xgmac_reg`; `xgmac_register_value` reads/writes `XGMAC_IOREAD/IOWRITE` at that offset.
- XPCS files: `xpcs_mmd`, `xpcs_register`, and `xpcs_register_value` select an MMD/register pair and read/write through `XMDIO_READ/WRITE`.
- Optional XPROP files: `xprop_register` and `xprop_register_value` use `XP_IOREAD/IOWRITE` when `pdata->xprop_regs` exists.
- Optional XI2C files: `xi2c_register` and `xi2c_register_value` use `XI2C_IOREAD/IOWRITE` when `pdata->xi2c_regs` exists.
- Optional booleans: `an_cdr_workaround` and `an_cdr_track_early` expose runtime workaround flags if the variant data enables the CDR workaround.
- `xgbe_debugfs_init()`, `xgbe_debugfs_exit()`, and `xgbe_debugfs_rename()` manage the debugfs directory lifecycle.

## Control Flow

Initialization sets default selector values, creates a directory named `amd-xgbe-%s`, then creates register selector and value files with mode `0600`. A read of a selector file returns the cached selector. A write to a selector file updates the cached offset or MMD. A read of a value file performs the current hardware access and returns the result. A write to a value file parses a hex value and writes it to the selected register.

Directory teardown is a single recursive debugfs removal. Rename updates the directory name after netdev rename using `debugfs_change_name`.

## State and Persistence Behavior

Persistent state is limited to selector fields in `struct xgbe_prv_data`: `debugfs_xgmac_reg`, `debugfs_xpcs_mmd`, `debugfs_xpcs_reg`, `debugfs_xprop_reg`, and `debugfs_xi2c_reg`, plus the workaround booleans. These are runtime-only and reset on device reprobe or driver unload. Hardware writes performed through debugfs mutate live device state and can survive until reset or later driver reconfiguration.

## Dependencies and Integration Points

The file depends on Linux debugfs, module ownership, simple read/write helpers, slab allocation, and xgbe register macros from `xgbe-common.h`. It integrates with the probe/remove/rename lifecycle through calls from the broader driver. XPCS value access goes through `pdata->hw_if.read_mmd_regs`/`write_mmd_regs`, so it shares locking and platform-specific access semantics from `xgbe-dev.c`.

## Risks and Failure Modes

- There is no range validation for register offsets. A privileged writer can select offsets outside the intended documented register range for a mapped block.
- Register value writes can disrupt a live data path, link training, I2C transactions, timestamping, or interrupt behavior.
- The selector/value sequence is not atomic across users. Concurrent debugfs users can change a selector between another user's selector write and value read/write.
- `xgbe_common_write()` treats parse failures as `-EIO`; scripts may need to distinguish invalid input from hardware failures separately.
- `xgbe_debugfs_init()` does not check each `debugfs_create_file()` result, which is typical for debugfs but means missing entries may only be noticed by inspection.

## Test Signals

Mount debugfs and verify directory creation, rename after netdev rename, and cleanup on device removal. Read XGMAC feature or version registers through the selector/value pair and compare with driver logs. Exercise XPCS reads against known MMD registers. Negative tests should include too-small read buffers, nonzero write offsets, overlong writes, invalid hex input, and concurrent selector changes. Avoid destructive value writes except on disposable hardware or with a documented register plan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-desc.c

## Purpose

`xgbe-desc.c` owns descriptor-ring memory management and packet buffer DMA mapping for the AMD XGBE driver. It allocates coherent descriptor rings and per-descriptor metadata, prepares RX page-backed buffers, maps TX skb data into DMA segments, releases DMA mappings and page references, and installs the descriptor-interface function table used by the runtime driver.

The file is the resource-management layer between Linux skbs/pages and hardware descriptor programming in `xgbe-dev.c`.

## Important APIs and Functions

- `xgbe_alloc_ring_resources()` allocates TX and RX ring descriptors/metadata for every active channel.
- `xgbe_free_ring_resources()` and `xgbe_free_ring()` unmap all per-descriptor resources, free metadata, free page pools, and free coherent descriptor memory.
- `xgbe_init_ring()` allocates one DMA-coherent `struct xgbe_ring_desc` array and one `struct xgbe_ring_data` array for a ring.
- `xgbe_alloc_pages()` allocates node-preferred compound pages, falls back to smaller orders and any NUMA node, and maps pages for device RX.
- `xgbe_set_buffer_data()` slices a shared page allocation into per-descriptor buffer descriptors and records which descriptor is responsible for unmapping an exhausted page allocation.
- `xgbe_map_rx_buffer()` ensures header and payload page allocations exist, then assigns RX header and buffer DMA slices to a descriptor.
- `xgbe_wrapper_tx_descriptor_init()` and `xgbe_wrapper_rx_descriptor_init()` populate descriptor pointers/DMA addresses in metadata, reset ring indices, and call hardware descriptor init hooks.
- `xgbe_unmap_rdata()` is the common cleanup routine for TX skb DMA, skb ownership, RX page references, RX DMA unmap ownership, saved RX packet state, and metadata reset.
- `xgbe_map_tx_skb()` maps an skb into one or more TX descriptors, including optional context descriptor reservation, TSO header mapping, linear payload segmentation, and fragmented skb page mapping.
- `xgbe_init_function_ptrs_desc()` publishes the descriptor operations through `struct xgbe_desc_if`.

## Control Flow

Open/start allocates channels elsewhere, then `alloc_ring_resources` walks each channel and initializes TX and RX rings. RX descriptor wrapper initialization maps buffers for every descriptor before giving the ring to hardware. For RX, header pages are order-0 and payload pages use `PAGE_ALLOC_COSTLY_ORDER` when possible; the driver can allocate separate header buffers for split-header/checksum mode or full-size header buffers when RX checksum offload is disabled.

Transmit starts in `xgbe-drv.c`, which computes required descriptors and calls `map_tx_skb`. This function reserves room for a context descriptor when TSO MSS or VLAN tag state must change, maps the TSO header separately if needed, maps the linear skb data in chunks no larger than `XGBE_TX_MAX_BUF_SIZE`, maps each skb fragment in chunks, stores the skb pointer in the final mapped descriptor, and returns the descriptor count. On any DMA mapping failure, it unmaps all descriptors mapped since the starting index and returns zero.

Cleanup paths call `unmap_rdata` whether descriptors are being reclaimed after TX completion, recycled after RX, or freed during close/restart. The cleanup routine deliberately handles both TX and RX state because the same metadata type backs both ring kinds.

## State and Persistence Behavior

The file persists ring state in `struct xgbe_ring`: descriptor count, coherent descriptor base/DMA address, metadata array, RX page allocation cursors, current and dirty indices, TX cached context state, and packet metadata. Per-descriptor state lives in `struct xgbe_ring_data`: descriptor pointer/DMA address, TX skb DMA mapping, RX buffer page references, RX state saved across NAPI budget exits, and packet accounting. All state is runtime-only and rebuilt on open, full restart, ring-count changes, and memory reallocation.

## Dependencies and Integration Points

Dependencies include DMA mapping APIs, page allocation/refcount APIs, skb fragment DMA helpers, NUMA allocation helpers, and the xgbe ring/channel/private structures. The file integrates with:

- `xgbe-drv.c` for open/close memory allocation, TX mapping, RX refresh, and cleanup.
- `xgbe-dev.c` for hardware descriptor initialization and descriptor reset callbacks.
- NAPI RX paths that may save partial-packet state in `rdata->state`.
- Netdev feature bits such as `NETIF_F_RXCSUM`, which influence RX split-header buffer sizing.

## Risks and Failure Modes

- On `xgbe_init_ring()` failure after descriptor allocation but before metadata allocation, cleanup is left to the caller's error path; the caller does call `xgbe_free_ring_resources`, so this ordering must remain intact.
- RX page-slicing correctness depends on `pa_unmap` ownership being assigned exactly when an allocation is exhausted. Refcount or unmap mistakes would produce page leaks, double unmaps, or DMA lifetime bugs.
- `xgbe_map_tx_skb()` assumes ring space was already checked by `xgbe_maybe_stop_tx_queue`; callers must keep descriptor count calculation in sync with mapping behavior.
- TSO and VLAN context reservation uses cached ring context. Incorrect cache state can under-reserve descriptors or emit stale context.
- DMA mapping failures are handled, but repeated failures can drop packets and should be visible through netdev alerts or TX errors.

## Test Signals

Stress TX with linear, fragmented, TSO, VLAN-tagged, and VXLAN/GSO skbs while watching DMA mapping warnings, descriptor leaks, and queue stalls. Stress RX under small MTU, jumbo MTU, RX checksum on/off, and low-memory conditions. Use driver unload/reload and repeated open/close to catch page/DMA leaks. KASAN, DMA_API_DEBUG, page refcount diagnostics, and high-throughput NAPI tests are strong signals for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dev.c

## Purpose

`xgbe-dev.c` is the low-level hardware programming layer for AMD XGBE. It configures DMA, MTL queues, MAC filtering, VLAN, RSS, flow control, DCB, ECC, MDIO/XPCS access, descriptors, TX/RX enablement, timestamp/MMC counter handling, and device reset. It also publishes the `struct xgbe_hw_if` function table consumed by the netdev driver, PHY code, ethtool paths, DCB, debugfs, and PTP support.

The file translates driver-private state into concrete XGMAC register writes and descriptor bitfields using `xgbe-common.h`.

## Important APIs and Functions

- Hardware feature/config: `xgbe_init()`, `xgbe_exit()`, `xgbe_config_dma_bus()`, `xgbe_config_dma_cache()`, `xgbe_config_mtl_mode()`, `xgbe_config_queue_mapping()`, FIFO sizing, flow-control thresholds, and `xgbe_set_speed()`.
- Descriptor programming: `xgbe_tx_desc_init()`, `xgbe_rx_desc_init()`, `xgbe_tx_desc_reset()`, `xgbe_rx_desc_reset()`, `xgbe_tx_start_xmit()`, `xgbe_dev_xmit()`, and `xgbe_dev_read()`.
- Interrupt control: `xgbe_enable_dma_interrupts()`, MAC/MTL/ECC interrupt setup, and per-channel `xgbe_enable_int()`/`xgbe_disable_int()`.
- RSS/VXLAN: RSS key/table programming through `MAC_RSSAR/RSSDR`, feature-gated RSS enable/disable, VXLAN tunnel ID setup and tunneling enablement.
- Flow control/DCB: TX/RX pause configuration, PFC queue detection, FIFO distribution, DCB ETS traffic class programming, PFC reconfiguration, and netdev TC mapping.
- MAC/VLAN/filtering: MAC address programming, hash/perfect filter setup, promiscuous/all-multicast handling, VLAN hash table, VLAN stripping/filtering, jumbo mode, checksum offload.
- MDIO/XPCS: V1/V2 MMIO windowed XPCS access, V3 SMN-based access, external clause 22/45 MDIO reads/writes with completion wait, and MDIO mode selection.
- MMC/statistics: counter read width handling, interrupt accumulation, freeze/read/unfreeze bulk stats, and counter reset-on-read configuration.
- Lifecycle/export: `xgbe_init_function_ptrs_dev()` fills `struct xgbe_hw_if`; `xgbe_enable_mac_loopback()` and `xgbe_disable_mac_loopback()` support loopback tests.

## Control Flow

Device initialization flushes TX queues, configures DMA bus/cache/PBL/coalescing/buffer sizes/TSO/SPH/RSS, initializes descriptor rings, enables DMA interrupts, configures MTL scheduling/queue mapping/store-forward/thresholds/FIFOs/DCB, configures MAC address/filtering/jumbo/flow-control/speed/checksum/VLAN/MMC, then enables MAC and ECC interrupts. This path is called from `xgbe-drv.c` during start and restart.

TX control flow begins after `xgbe-drv.c` maps skb data. `xgbe_dev_xmit()` optionally emits a context descriptor for changed TSO MSS or VLAN tag, fills normal descriptors with DMA addresses and lengths, sets checksum/TSO/VLAN/PTP/VXLAN bits, accounts packet/byte totals, applies memory barriers, gives the first descriptor to hardware by setting OWN, advances `ring->cur`, and either rings the DMA tail pointer immediately or defers via `xmit_more`.

RX control flow reads the current descriptor, checks OWN, handles timestamp context descriptors, extracts first/last/context flags, split-header length, RSS hash/type, packet length, checksum and tunnel status, VLAN tag, error status, and per-queue accounting. The NAPI layer in `xgbe-drv.c` uses this parsed packet state to assemble skbs and recycle descriptors.

MDIO/XPCS access is selected by `pdata->vdata->xpcs_access`. V1 and V2 use MMIO window selection guarded by `xpcs_lock`; V3 uses AMD SMN reads/writes and updates halfwords within a 32-bit SMN word. External MDIO operations use MAC MDIO command registers and wait on `pdata->mdio_complete`, which is completed by the MAC interrupt path.

## State and Persistence Behavior

Most persistent runtime state is in `struct xgbe_prv_data`: hardware feature flags, queue counts, FIFO sizing limits, DCB policy pointers, PFC queue flags, RSS key/table/options, active VLAN bitmap, flow-control threshold arrays, cached netdev features, VXLAN port, PHY speed, interrupt mode, coalescing settings, and MMC stats. Ring-local persistent state includes cached TSO MSS and VLAN tag context plus coalescing counters. Hardware register state is volatile and reconstructed by `xgbe_init()` after reset, open, and restart.

Counters in `pdata->mmc_stats` accumulate hardware MMC values read on interrupt and stats queries. The code freezes counters for bulk reads and uses reset-on-read mode, making the software structure the long-lived counter accumulator.

## Dependencies and Integration Points

The file depends on kernel PHY/MDIO, PCI/SMN access, clocks, CRC helpers, bit reversal, netdev feature bits, VLAN/RSS/VXLAN concepts, DMA descriptor definitions, and xgbe private interfaces. It integrates with:

- `xgbe-drv.c` through `struct xgbe_hw_if` for open/close, TX/RX, NAPI, feature changes, stats, and restart.
- `xgbe-desc.c` through descriptor init/reset and mapped descriptor metadata.
- `xgbe-dcb.c` through DCB TC/PFC hardware callbacks.
- PTP timestamp helpers such as `xgbe_get_rx_tstamp()` and `xgbe_get_tx_tstamp()`.
- PHY and debugfs paths through MMD/MDIO register access.
- Netdev VLAN, RSS, checksum, GSO/VXLAN, and traffic-class feature APIs.

## Risks and Failure Modes

- Register programming order is critical. DMA/descriptor ownership barriers, tail-pointer writes, MAC/MTL/DMA enable order, and reset polling must remain correct to avoid hangs.
- MDIO completion relies on MAC interrupts. If interrupts are disabled or misrouted, external MDIO reads/writes time out.
- XPCS V3 SMN read-modify-write must preserve the opposite halfword. Bad offset handling can corrupt adjacent PCS registers.
- FIFO and PFC calculations depend on MTU, TC count, queue count, and delay estimates. Wrong thresholds can cause pause storms, loss where lossless is expected, or underutilized RX FIFO.
- RX parsing trusts descriptor status fields but contains length-underflow guards. Any hardware erratum around descriptor fields can surface as drops or checksum misclassification.
- RSS programming is serialized by `rss_mutex`, but callers must still ensure feature changes and device reset do not race in unsupported ways.
- `xgbe_disable_tx()` waits for DMA completion and queue drain; link-down cases are specially handled by returning early in completion wait and later cleanup paths. This reduces shutdown stalls but makes packet accounting and descriptor cleanup behavior important.

## Test Signals

Exercise full open/close/restart, MTU changes, TX/RX under load, TSO/checksum/VLAN/VXLAN offloads, RSS enable/disable and indirection changes, DCB/PFC policy changes, pause negotiation, MDIO access, PTP timestamping, hardware stats, ECC interrupt injection if available, and MAC loopback. Watch for DMA API warnings, descriptor ownership stalls, MDIO timeouts, NAPI budget livelocks, wrong RSS hashes, VLAN filter misses, bad MMC counter deltas, and timeout messages from TX/RX stop paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-drv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-drv.c

## Purpose

`xgbe-drv.c` is the main Linux netdev runtime for the AMD XGBE driver. It owns channel allocation, open/close, IRQ and NAPI orchestration, service timers, ECC handling, powerdown/powerup, TX skb preparation, RX skb assembly, stats exposure, feature toggles, traffic-class setup, VLAN notifications, VXLAN UDP tunnel registration, restart/stop work, and debug packet/descriptor dumps.

This file coordinates high-level kernel networking lifecycles with the hardware callbacks implemented in `xgbe-dev.c` and descriptor resource callbacks implemented in `xgbe-desc.c`.

## Important APIs and Functions

- Channel/memory lifecycle: `xgbe_alloc_channels()`, `xgbe_free_channels()`, `xgbe_alloc_memory()`, `xgbe_free_memory()`, TX/RX data cleanup, and coalescing initialization.
- Device lifecycle: `xgbe_open()`, `xgbe_close()`, `xgbe_start()`, `xgbe_stop()`, `xgbe_restart_dev()`, `xgbe_full_restart_dev()`, `xgbe_powerdown()`, and `xgbe_powerup()`.
- IRQ/NAPI: `xgbe_request_irqs()`, `xgbe_free_irqs()`, `xgbe_isr()`, `xgbe_isr_bh_work()`, `xgbe_dma_isr()`, `xgbe_ecc_isr()`, `xgbe_one_poll()`, and `xgbe_all_poll()`.
- Timers/work: service timer/work for PHY status, per-channel TX timers for coalescing, restart work, stop-device work, ECC bottom-half work, and TX timestamp work.
- TX path: `xgbe_xmit()`, `xgbe_packet_info()`, `xgbe_prep_tso()`, `xgbe_prep_vlan()`, `xgbe_is_tso()`, `xgbe_is_vxlan()`, descriptor availability checks, and queue stop/wake logic.
- RX path: `xgbe_rx_poll()`, `xgbe_rx_refresh()`, `xgbe_create_skb()`, buffer length helpers, checksum/VLAN/RSS/timestamp/tunnel skb annotation, and GRO delivery.
- Netdev operations: `xgbe_netdev_ops` includes open/stop/start_xmit/set_rx_mode/set_mac/change_mtu/tx_timeout/get_stats64/VLAN add-kill/setup_tc/fix_features/set_features/features_check/hwtstamp hooks.
- Hardware discovery and tunnels: `xgbe_get_all_hw_features()` decodes feature registers; `xgbe_get_udp_tunnel_info()` exposes one VXLAN port table.
- Diagnostics: `xgbe_dump_tx_desc()`, `xgbe_dump_rx_desc()`, and `xgbe_print_pkt()`.

## Control Flow

Open creates device and auto-negotiation workqueues, enables clocks, initializes work items and PTP, allocates rings/descriptors, starts hardware, and clears the DOWN state. Start sets real TX/RX queue counts, prepares the RSS table, calls `hw_if->init`, enables NAPI, requests IRQs, resets and starts PHY, enables TX/RX, resets UDP tunnel state, starts queues and timers, queues initial service work, and clears STOPPED.

Stop is the reverse operational path: stop TX queues, drop carrier, stop timers, flush work, disable VXLAN, disable TX/RX, stop PHY, free IRQs, disable/delete NAPI, reset hardware, reset netdev TX queues, and set STOPPED. Close then frees memory, disables clocks, destroys workqueues, and sets DOWN. Restart variants either preserve allocated rings while freeing packet data or fully free/reallocate memory for ring-count changes.

The shared interrupt handler reads DMA status, schedules either global or per-channel NAPI for TX/RX/RBU work, handles fatal bus error by scheduling restart, services MAC MMC/timestamp/MDIO interrupts, and invokes AN/ECC/I2C handlers when those IRQs share the device line. Per-channel DMA interrupts schedule the channel NAPI directly. ECC bottom-half handling rate-limits corrected errors, disables noisy SEC sources, and stops the device on repeated detected errors.

Transmit prepares packet metadata, checks descriptor availability, performs TSO header preparation, maps the skb through `desc_if->map_tx_skb`, prepares TX timestamping, accounts bytes to BQL, and delegates descriptor programming to `hw_if->dev_xmit`. RX polling repeatedly asks `hw_if->dev_read` to parse descriptors, builds skbs from header and page-frag buffers, preserves partial packet state across budget exits, validates MTU, annotates checksum/tunnel/VLAN/timestamp/RSS metadata, and submits packets through GRO.

## State and Persistence Behavior

Driver state lives in `struct xgbe_prv_data`, channels, rings, timers, workqueues, NAPI structures, and statistics structures. Runtime state includes channel affinity/IRQ mappings, ring indices, queue-stopped flags, coalescing settings, ECC error periods/counts, power-down status, workqueue handles, active VLAN bitmap, netdev feature cache, VXLAN port, PTP timestamp work state, and `dev_state` flags such as DOWN/STOPPED.

No state is persisted outside the running kernel. Hardware and ring state is rebuilt on open and restart. Module parameters for ECC thresholds are persistent only for the loaded module instance and are exposed when ECC support is compiled in.

## Dependencies and Integration Points

The file integrates with core Linux networking APIs: netdev operations, NAPI, BQL, GRO, VLAN, GSO/TSO, UDP tunnel offload, traffic control mqprio, ethtool hwtstamp hooks, netpoll, PHY status, workqueues, timers, IRQ management, CPU/NUMA affinity, clocks, and module parameters. It depends heavily on `pdata->hw_if`, `pdata->desc_if`, `pdata->phy_if`, and `pdata->i2c_if` being initialized by sibling driver modules before open.

## Risks and Failure Modes

- NAPI/IRQ ordering is delicate. Interrupts are disabled before scheduling and re-enabled after `napi_complete_done`; mistakes cause interrupt storms or lost RX/TX completions.
- Global-NAPI mode divides budget by RX ring count. A zero or inconsistent `rx_ring_count` would be fatal; queue count setup must precede polling.
- TX descriptor count calculation must stay synchronized with `xgbe-desc.c` mapping and `xgbe-dev.c` descriptor emission.
- Link-down TX cleanup intentionally force-frees stuck descriptors without counting them as wire transmissions. This improves recovery but must not double-free skbs or over-report BQL completions.
- `xgbe_service_timer()` uses faster 100 ms polling while carrier is up and 1 s while down. That improves link-down detection but increases timer/service workload while the link is healthy.
- Stop/restart paths combine workqueue flushing, timer deletion, NAPI disable, IRQ free, PHY stop, and hardware reset; races here can surface as use-after-free, dead workqueue callbacks, or stuck queues.
- Feature changes can schedule restarts while toggling hardware bits. Callers must be under normal netdev serialization, and hardware callbacks must tolerate live state.

## Test Signals

Broad validation should include open/close loops, suspend-like powerdown/powerup, ring-count changes, MTU changes, traffic under TX/RX checksum offloads, TSO/GSO, VLAN add/remove/filtering, VXLAN tunnel registration, RSS, DCB traffic classes, PTP TX/RX timestamping, netpoll, link flap, fatal-bus/ECC recovery if injectable, and IRQ modes with and without per-channel interrupts. Monitor BQL, queue stop/wake logs, NAPI completion, DMA API checks, workqueue lifetime warnings, `tx_timeout`, MMC stats consistency, and packet drops during link transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-drv.c -->
