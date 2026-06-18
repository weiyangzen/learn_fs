# subset-b-004553 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/vport.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/vport.c

## Purpose
`vport.c` is the mlx5 core vport command helper layer. It marshals firmware command mailboxes for NIC and HCA vport state, MAC/MTU/filter lists, GUIDs, GID/P_Key tables, promiscuous and local loopback policy, RoCE enablement, vport counters, multiport affiliation, VHCA ID lookup, and other-function HCA capability get/set.

## Important APIs, types, and functions
The file exposes exported helpers such as `mlx5_query_vport_state()`, `mlx5_modify_vport_admin_state()`, `mlx5_modify_vport_max_tx_speed()`, `mlx5_query_nic_vport_mac_address()`, `mlx5_modify_nic_vport_mac_address()`, `mlx5_query_nic_vport_mtu()`, `mlx5_modify_nic_vport_mtu()`, `mlx5_query_nic_vport_mac_list()`, `mlx5_modify_nic_vport_mac_list()`, `mlx5_modify_nic_vport_vlans()`, `mlx5_query_hca_vport_gid()`, `mlx5_query_hca_vport_pkey()`, `mlx5_query_hca_vport_context()`, `mlx5_core_modify_hca_vport_context()`, `mlx5_core_query_vport_counter()`, and `mlx5_vport_get_other_func_cap()`. Shared state is mainly `struct mlx5_core_dev`, `struct mlx5_hca_vport_context`, `mdev->roce.roce_en`, and cached `mdev->sys_image_guid`. Command buffers use generated `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` accessors.

## Control Flow and State
Most functions allocate or stack-build an input mailbox, set opcode/op_mod/vport fields, optionally set `other_vport`, execute a firmware command through `mlx5_cmd_exec*()`, and copy selected fields into caller-owned objects. Capability gates protect cross-vport operations: non-manager attempts to query or modify other vports return `-EPERM` or `-EACCES`. List updates size buffers from firmware capability limits and fail with `-ENOSPC` if caller-supplied MAC/VLAN lists exceed supported sizes.

The main persistent behavior is firmware state mutation: vport admin state, speed cap, MAC address, MTU, allowed UC/MC/VLAN lists, promiscuous bits, local loopback disable bits, HCA vport context fields, RoCE enable bit, and multiport affiliation. Software state is small but important: `mlx5_roce_en_lock` serializes RoCE reference count transitions, multiport affiliation enables RoCE before setting affiliation and disables it on unwind, and `mlx5_query_nic_system_image_guid()` caches the queried GUID on `mdev`.

## Dependencies and Integration Points
The file integrates with mlx5 command infrastructure, generated IFC layouts, eswitch helpers for vport-to-function/VHCA ID mapping, SF support, InfiniBand GID/P_Key types, Ethernet address helpers, and exported symbols consumed by mlx5e, eswitch, RDMA, devlink, SR-IOV, and multiport code.

## Risks and Test Signals
Risks include incorrect `other_vport` selection, off-by-one VF/vport/function IDs, capability gating regressions, memory allocation failures in dynamic mailboxes, missed RoCE reference restoration on command failure, and firmware-visible list size mismatches. Useful tests are kernel build coverage, mlx5 probe with PF/VF/SF/eCPF variants, SR-IOV vport state and MAC/MTU changes, UC/MC/VLAN list programming, RoCE enable/disable nesting, multiport affiliate/unaffiliate rollback, devlink/eswitch counter queries, and negative tests for non-manager cross-vport access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/vport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wc.c

## Purpose
`wc.c` probes whether mlx5 BlueFlame write-combining doorbells are usable on the platform. It builds a temporary CQ/SQ pair, posts NOP WQEs through a BF register using write-combining style MMIO copies, polls the CQ, and records `mdev->wc_state` as supported or unsupported.

## Important APIs, Types, and Functions
Local types `struct mlx5_wc_cq` and `struct mlx5_wc_sq` combine mlx5 work queues, core CQ/SQ IDs, BlueFlame register allocation, producer/consumer counters, and control resources. Key helpers are `mlx5_wc_create_cq()`, `create_wc_cq()`, `mlx5_wc_create_sq()`, `create_wc_sq()`, `mlx5_iowrite64_copy()`, `mlx5_wc_post_nop()`, `mlx5_wc_poll_cq()`, `mlx5_core_test_wc()`, and exported `mlx5_wc_support_get()`.

## Control Flow and State
`mlx5_wc_support_get()` first checks BlueFlame and SQ capabilities, then serializes the one-time test with `mdev->wc_state_lock`. SF devices reuse the parent device's state. The test allocates a BFREG, creates a CQ, creates a cyclic SQ, posts 254 unsignaled NOPs and one signaled NOP, polls for a CQE for up to 100 ms, and marks support according to the returned WQE counter. Destroy paths release SQ, CQ, BFREG, WQ buffers, and doorbell records in reverse order.

State is deliberately persistent for the device lifetime in `mdev->wc_state`, so later callers avoid re-running the hardware test. Posting uses DMA and CPU ordering barriers: WQE contents are written before the doorbell record, the doorbell record before the MMIO BF copy, and CQ doorbell updates before new CQEs are enabled.

## Dependencies and Integration Points
The file depends on mlx5 CQ/SQ creation commands, the common WQ helpers in `wq.c`, BlueFlame register allocation, clock timestamp-format helpers, PCI/MMIO I/O APIs, polling helpers, and optional ARM64 kernel-mode NEON for a 64-byte SIMD store path.

## Risks and Test Signals
Risks include leaking temporary CQ/SQ resources on partial failure, misdetecting write-combining due to CQ polling timeout, wrong CQE stride handling on 128-byte CQEs, architecture-specific SIMD store bugs, and incorrect state sharing between SFs and parents. Test signals include build coverage with and without ARM64 NEON, mlx5 probe on BF-capable and non-BF hardware, SF WC state propagation, fault injection for CQ/SQ/BFREG allocation failures, and logs showing either supported state or the warning that write combining is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.c

## Purpose
`wq.c` implements allocation, initialization, reset, debug dumping, and destruction for mlx5 work queue memory layouts: cyclic WQs, QP send/receive WQs, completion queues, and linked-list WQs.

## Important APIs, Types, and Functions
Public helpers are `mlx5_wq_cyc_create()`, `mlx5_wq_cyc_wqe_dump()`, `mlx5_wq_cyc_reset()`, `mlx5_wq_qp_create()`, `mlx5_cqwq_create()`, `mlx5_wq_ll_create()`, `mlx5_wq_ll_reset()`, and `mlx5_wq_destroy()`. They fill `struct mlx5_wq_ctrl`, `struct mlx5_wq_cyc`, `struct mlx5_wq_qp`, `struct mlx5_cqwq`, and `struct mlx5_wq_ll` defined in `wq.h`.

## Control Flow and State
Each create path allocates a doorbell record with `mlx5_db_alloc_node()`, allocates fragmented queue memory with `mlx5_frag_buf_alloc_node()` on the requested NUMA node, initializes a fragment-buffer controller with queue stride/size fields extracted from firmware context structures, and stores `wq_ctrl->mdev` for later destruction. QP creation partitions one allocation between RQ and SQ, using an offset if the RQ occupies less than a page and a fragment-array offset otherwise. Linked-list WQs initialize every WQE's next pointer and remember the tail link for pop operations.

Reset functions zero producer counters and current size, rebuild the linked free list where relevant, and update doorbell records. `mlx5_wq_cyc_wqe_dump()` is ratelimited and dumps raw WQE bytes for diagnostics. State is in coherent/fractured queue memory, doorbell records, queue counters, and linked next pointers; no disk-persistent state exists.

## Dependencies and Integration Points
The file depends on mlx5 fragmented buffer allocation, doorbell records, generated context access macros, WQE/CQE definitions, and callers across mlx5e, core CQ/SQ handling, RDMA, and test code such as `wc.c`.

## Risks and Test Signals
Risks include mismatched log sizes/strides, wrong SQ/RQ offset math for QP queues, failure unwind leaks, stale doorbell records after reset, linked-list tail corruption, and consumers using full/missing counters inconsistently. Tests should cover mlx5 driver build, queue creation/destruction in probe/open/close paths, allocation failure injection, WQE dump paths, CQ/SQ/RQ traffic, QP layout cases with sub-page and multi-page RQ sizes, and DMA/debug checks for queue buffer access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.h

## Purpose
`wq.h` is the shared mlx5 work queue API and inline cursor library. It declares queue allocation helpers and defines fast-path operations for cyclic WQs, completion WQs, and linked-list WQs.

## Important APIs, Types, and Functions
Core types are `struct mlx5_wq_param`, `struct mlx5_wq_ctrl`, `struct mlx5_wq_cyc`, `struct mlx5_wq_qp`, `struct mlx5_cqwq`, and `struct mlx5_wq_ll`. Inline APIs expose size, full/empty/missing tests, producer/consumer counter conversion, WQE/CQE pointer lookup, doorbell record updates, push/pop operations, wrap-count ownership checks, enhanced CQE validity checks, and linked-list next-pointer operations.

## Control Flow and State
The header has no top-level runtime flow, but its inlines are fast-path control flow. Cyclic WQs use `wqe_ctr` and `cur_sz` to derive head and tail through a power-of-two mask. CQ WQs use `cc` and owner/validity bits to decide whether hardware has produced a CQE, then issue `dma_rmb()` before returning readable contents. Linked-list WQs use `head`, `tail_next`, `wqe_ctr`, and `cur_sz` so software can push posted WQEs and relink completed/free entries.

## Dependencies and Integration Points
It depends on mlx5 IFC structures, CQ/QP definitions, fragment-buffer helpers, byte-order conversion, DMA barriers, and WQE structures such as `struct mlx5_wqe_srq_next_seg`. It is included by mlx5 core, Ethernet, RDMA, and test code that owns queue objects.

## Risks and Test Signals
Risks are concentrated in wrap arithmetic and ordering: off-by-one full checks, 16-bit cyclic counter comparisons, CQE ownership validation, missing DMA barriers, 128-byte CQE pointer adjustment, and linked-list relinking. Build coverage catches prototype drift, while runtime signals include clean TX/RX/CQ operation under wraparound, CQ overrun absence, no stale CQE reads on weakly ordered CPUs, and queue state correctness after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Kconfig

## Purpose
This Kconfig entry exposes the Mellanox/NVIDIA BlueField Gigabit Ethernet management-port driver as `CONFIG_MLXBF_GIGE`.

## Important APIs, Types, and Functions
It defines a tristate symbol named `MLXBF_GIGE` with prompt text for BlueField Gigabit Ethernet support. It depends on `(ARM64 && ACPI) || COMPILE_TEST` and selects `PHYLIB`.

## Control Flow and State
There is no runtime control flow. Build-time selection controls whether `mlxbf_gige.o` is compiled built-in, as a module, or not at all. The dependency expresses that the real hardware path is ACPI-described ARM64 BlueField, while `COMPILE_TEST` keeps broad build coverage possible.

## Dependencies and Integration Points
The symbol is consumed by the local Makefile and integrates with Linux PHYLIB, ACPI platform-device discovery, and the Mellanox Ethernet menu hierarchy.

## Risks and Test Signals
Risks include missing dependencies for APIs used by the driver or over-restricting build coverage. Test signals are `allyesconfig`/`allmodconfig` and `COMPILE_TEST` builds, ARM64 ACPI platform builds, and verifying that enabling the symbol pulls in PHYLIB and compiles all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Makefile

## Purpose
This Makefile assembles the BlueField Gigabit Ethernet driver from its functional source files when `CONFIG_MLXBF_GIGE` is enabled.

## Important APIs, Types, and Functions
It builds `mlxbf_gige.o` from `mlxbf_gige_ethtool.o`, `mlxbf_gige_intr.o`, `mlxbf_gige_main.o`, `mlxbf_gige_mdio.o`, `mlxbf_gige_rx.o`, and `mlxbf_gige_tx.o`.

## Control Flow and State
There is no runtime flow. Link order ensures the module contains ethtool operations, IRQ handlers, platform/netdev lifecycle, MDIO support, and RX/TX fast paths in one object.

## Dependencies and Integration Points
The object is controlled by the Kconfig symbol and links against kernel networking, PHY, platform, DMA, and IRQ APIs referenced by the component files.

## Risks and Test Signals
Risks are missing new source files from `mlxbf_gige-y`, stale object names after file renames, or accidental inclusion of objects that require unmet Kconfig dependencies. Test signals are kernel builds with `CONFIG_MLXBF_GIGE=y` and `m`, module load symbol resolution, and static link checks for `mlxbf_gige_ethtool_ops` and `mlxbf_gige_start_xmit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige.h

## Purpose
`mlxbf_gige.h` is the internal contract for the BlueField GigE management-port driver. It defines queue sizes, DMA alignment constants, MAC filter indexes, interrupt indexes, register parameter descriptors, MDIO gateway abstraction, link configuration callbacks, private device state, WQE/CQE bit layouts, ACPI resource indexes, and cross-file prototypes.

## Important APIs, Types, and Functions
Key structures are `struct mlxbf_gige_stats`, `struct mlxbf_gige_reg_param`, `struct mlxbf_gige_mdio_gw`, `struct mlxbf_gige_link_cfg`, and `struct mlxbf_gige`. The private state holds MMIO bases, DMA rings, SKB arrays, indexes, IRQ numbers, PHY/MDIO objects, NAPI, stats, hardware version, MDIO gateway layout, and link speed cache. Prototypes connect main, RX, TX, IRQ, MDIO, and ethtool source files.

## Control Flow and State
The header has no direct runtime flow, but it defines the state machines used elsewhere. RX and TX rings use fixed maximum SKB arrays, coherent descriptor memory, producer/consumer indexes, and hardware CQE polarity. The driver assumes 2 KB packet buffers and a 4 KB DMA-page limitation, expressed through `MLXBF_GIGE_DEFAULT_BUF_SZ` and DMA page constants.

## Dependencies and Integration Points
It includes Linux netdevice, IRQ, PHY, and non-atomic 64-bit I/O headers. It integrates with the register map in `mlxbf_gige_regs.h`, version-specific MDIO headers, and all driver translation units.

## Risks and Test Signals
Risks include mismatched queue limits versus hardware programming, stale bit masks for WQE/CQE layouts, fixed-size SKB arrays not matching runtime queue sizes, and accidental changes to private state shared across files. Test signals are full driver build, ring open/close cycles, RX/TX wraparound, ethtool stats correctness, MDIO read/write on BF2 and BF3, and sparse/build warnings for prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_ethtool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_ethtool.c

## Purpose
`mlxbf_gige_ethtool.c` provides ethtool inspection and PHY settings for the BlueField GigE netdev, including register dumps, ring parameter reporting, private statistics, pause parameters, pause counters, and link settings delegated to PHYLIB.

## Important APIs, Types, and Functions
The exported object is `mlxbf_gige_ethtool_ops`. Helpers include `mlxbf_gige_get_regs_len()`, `mlxbf_gige_get_regs()`, `mlxbf_gige_get_ringparam()`, `mlxbf_gige_get_sset_count()`, `mlxbf_gige_get_strings()`, `mlxbf_gige_get_ethtool_stats()`, `mlxbf_gige_get_pauseparam()`, `mlxbf_gige_llu_counters_enabled()`, and `mlxbf_gige_get_pause_stats()`.

## Control Flow and State
Register dump copies the defined MMIO range from `priv->base`. Ring reporting returns driver maxima and current queue sizes. Stats output must remain synchronized with `mlxbf_gige_ethtool_stats_keys`; it mixes software-maintained error counters with live hardware counters for values cleared by port clean. Pause stats read LLU counters only if the BF2/BF3-specific LLU counter-enable bit is set.

## Dependencies and Integration Points
The file depends on netdev ethtool operations, PHYLIB ethtool helpers, `mlxbf_gige_regs.h` offsets, and `struct mlxbf_gige` state. It is installed during probe through `netdev->ethtool_ops`.

## Risks and Test Signals
Risks include stats key/data order drift, reading live counters while the port is reset, wrong BF2/BF3 pause-counter offsets, and exposing incomplete register ranges if the register map changes. Test signals are `ethtool -S`, `ethtool -d`, `ethtool -g`, pause frame traffic, BF2/BF3 LLU counter enable checks, and PHY link setting get/set through ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_intr.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_intr.c

## Purpose
`mlxbf_gige_intr.c` handles the BlueField GigE interrupt lines: error/status, receive packet, and LLU/PLU events.

## Important APIs, Types, and Functions
Local handlers are `mlxbf_gige_error_intr()`, `mlxbf_gige_rx_intr()`, and `mlxbf_gige_llu_plu_intr()`. Public helpers are `mlxbf_gige_request_irqs()` and `mlxbf_gige_free_irqs()`.

## Control Flow and State
Open calls `mlxbf_gige_request_irqs()`, which requests error, RX, then LLU/PLU IRQs and unwinds in reverse on failure. The error handler reads `MLXBF_GIGE_INT_STATUS`, increments software stats for asserted error bits, clears all asserted error bits except the RX receive-packet bit, and returns handled. The RX handler relies on hardware auto-masking the receive interrupt and schedules NAPI; polling later clears the mask bit. The LLU/PLU handler currently only acknowledges as handled.

## Dependencies and Integration Points
The file depends on Linux IRQ APIs, MMIO status registers, NAPI scheduling through `priv->napi`, and the stats fields exported through netdev and ethtool paths.

## Risks and Test Signals
Risks include clearing the RX bit from the wrong context, missing an error bit in stats, IRQ request unwind bugs, scheduling NAPI after stop, and an intentionally empty LLU/PLU handler masking future event needs. Test signals are interrupt request/free on open/close, RX interrupt-to-NAPI flow, induced TX/RX/SW/HW error status bits, IRQ storm absence, and stats increments visible through ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_main.c

## Purpose
`mlxbf_gige_main.c` owns the BlueField GigE platform and netdevice lifecycle. It probes ACPI resources, maps MMIO blocks, initializes MDIO/PHY, registers the netdev, opens and stops the port, manages reset/clean-port sequencing, sets MAC filters, provides netdev ops, handles link-mode policy for BF2/BF3, and detaches the interface during shutdown.

## Important APIs, Types, and Functions
Key helpers are `mlxbf_gige_alloc_skb()`, `mlxbf_gige_initial_mac()`, `mlxbf_gige_cache_stats()`, `mlxbf_gige_clean_port()`, `mlxbf_gige_open()`, `mlxbf_gige_stop()`, `mlxbf_gige_eth_ioctl()`, `mlxbf_gige_set_rx_mode()`, `mlxbf_gige_get_stats64()`, BF2/BF3 adjust-link and link-mode functions, `mlxbf_gige_probe()`, `mlxbf_gige_remove()`, and `mlxbf_gige_shutdown()`. `mlxbf_gige_netdev_ops` binds Linux netdev callbacks.

## Control Flow and State
Probe maps MAC/LLU/PLU resources, allocates `net_device`, initializes private state, reads hardware version, probes MDIO, disables filters/promiscuous mode, sets the initial MAC from hardware or random fallback, configures 64-bit DMA, obtains IRQs, finds and connects the PHY, applies version-specific link-mode restrictions, and registers the netdev. Open enables the port, caches counters that clean-port will clear, performs clean-port reset, resets RX polarity, starts PHY, initializes TX and RX rings, enables NAPI and the queue, requests IRQs, enables filters/multicast, and finally enables selected interrupts after a barrier. Stop disables interrupts, stops queue/NAPI, frees IRQs, stops PHY, tears down rings, caches stats, and cleans the port.

State persists in hardware registers, PHY state, DMA rings, `priv->valid_polarity`, MAC filter registers, cached stats, and `priv->prev_speed` for BF3 PLU reprogramming. `mlxbf_gige_alloc_skb()` enforces the hardware DMA alignment rule by overallocating and aligning packet data to a 2 KB boundary before mapping.

## Dependencies and Integration Points
The file depends on platform/ACPI resources, DMA APIs, netdevice registration, PHYLIB, NAPI, IRQ helpers in `mlxbf_gige_intr.c`, RX/TX setup, ethtool ops, and BF2/BF3 register definitions.

## Risks and Test Signals
Risks include unsupported `hw_version` indexing into link config, clean-port timeout, wrong resource order, PHY IRQ fallback behavior, missing unwind of MDIO/PHY/netdev resources, statistics lost across clean-port, and DMA alignment regressions. Test signals are ACPI probe, module load/unload, open/close cycles, shutdown path, random MAC fallback, BF2 and BF3 link negotiation, speed changes on BF3, ethtool/netdev stats, and fault injection for ring/IRQ/PHY failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio.c

## Purpose
`mlxbf_gige_mdio.c` implements the MDIO bus for BlueField GigE. It abstracts BF2 and BF3 MDIO gateway bit layouts, programs MDIO timing from core PLL registers, registers a `mii_bus`, and provides clause 22 read/write operations for the external PHY.

## Important APIs, Types, and Functions
The version table `mlxbf_gige_mdio_gw_t[]` maps gateway offsets and field masks into `struct mlxbf_gige_mdio_gw`. Important helpers are `calculate_i1clk()`, `mdio_period_map()`, `mlxbf_gige_mdio_create_cmd()`, `mlxbf_gige_mdio_read()`, `mlxbf_gige_mdio_write()`, `mlxbf_gige_mdio_cfg()`, `mlxbf_gige_mdio_probe()`, and `mlxbf_gige_mdio_remove()`.

## Control Flow and State
Probe rejects unsupported hardware versions, maps the MDIO resource, maps the shared clock resource or internal fallback resource, chooses the gateway table, configures MDC period and sampling registers, allocates a managed MDIO bus, installs read/write callbacks, and registers the bus. Reads and writes encode PHY address, register address, opcode, clause-22 start bit, data, and busy bit into the gateway register, poll until hardware clears busy, then clear the gateway register to release the MDIO lock. Reads fetch data from BF2's gateway register or BF3's separate data-read register.

State lives in gateway registers, timing configuration registers, `priv->mdio_io`, `priv->clk_io`, `priv->mdio_gw`, and the registered `mii_bus`. No firmware or disk-persistent state is written, but PHY register writes can alter link behavior.

## Dependencies and Integration Points
The file depends on platform resource mapping, raw MMIO access, polling helpers, PHYLIB `mii_bus`, ACPI-described resources, and BF2/BF3 MDIO layout headers. It feeds `phy_find_first()` and `phy_connect_direct()` in the main driver.

## Risks and Test Signals
Risks include wrong PLL-derived MDC timing, busy-bit timeout, failure to clear the gateway lock, BF2/BF3 mask/shift mismatches, resource conflicts on shared clock mapping, and only clause 22 support. Test signals include MDIO bus registration, PHY discovery, repeated MII reads/writes, timeout/error injection, BF2/BF3 timing register inspection, link negotiation, and clean remove/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf2.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf2.h

## Purpose
`mlxbf_gige_mdio_bf2.h` defines the BlueField-2 MDIO gateway and configuration register layout used by `mlxbf_gige_mdio.c`.

## Important APIs, Types, and Functions
It provides offsets `MLXBF2_GIGE_MDIO_GW_OFFSET` and `MLXBF2_GIGE_MDIO_CFG_OFFSET`, gateway masks/shifts for data/address, devad, partad, opcode, start bit, and busy bit, plus config masks for mode, 3.3 V, full drive, MDC period, input sample, and output sample. `MLXBF2_GIGE_MDIO_CFG_VAL` builds the static portion of the config value with `FIELD_PREP()`.

## Control Flow and State
The header has no runtime control flow. Its constants are consumed by the BF2 entry in `mlxbf_gige_mdio_gw_t[]` and by `mlxbf_gige_mdio_cfg()` when programming MDIO mode and timing.

## Dependencies and Integration Points
It depends on Linux bitfield helpers and integrates only with the BlueField GigE MDIO implementation.

## Risks and Test Signals
Risks are incorrect bit positions or default config values, which would break PHY access on BF2. Test signals are BF2 MDIO read/write success, PHY discovery, scope/register verification of MDC timing, and build coverage for the included header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf3.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf3.h

## Purpose
`mlxbf_gige_mdio_bf3.h` defines the BlueField-3 MDIO gateway, separate read-data register, and split configuration registers used by the shared MDIO code.

## Important APIs, Types, and Functions
It provides gateway/data/config offsets, masks and shifts for start, opcode, partad, devad, write data, busy, read data, mode, full drive, MDC period, input sample, and output sample. Unlike BF2, BF3 reads data from `MLXBF3_GIGE_MDIO_DATA_READ`.

## Control Flow and State
The header has no direct runtime control flow. `mlxbf_gige_mdio.c` uses these constants to build BF3 gateway commands and to write `CFG_REG0`, `CFG_REG1`, and `CFG_REG2` during MDIO setup.

## Dependencies and Integration Points
It depends on bitfield helpers and integrates with the BF3 hardware-version branch in the MDIO driver.

## Risks and Test Signals
Risks include confusing write-data and read-data fields, using BF2 timing layout on BF3, or wrong sampling constants. Test signals are BF3 PHY discovery, MII read/write loops, link negotiation at 10/100/1000, and register dumps confirming expected MDIO config programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio_bf3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_regs.h

## Purpose
`mlxbf_gige_regs.h` is the BlueField GigE register map for MAC control, interrupts, RX/TX ring programming, filters, counters, RX DMA, BF3 PLU SGMII speed programming, and BF2/BF3 LLU pause counters.

## Important APIs, Types, and Functions
It defines offsets and bit masks for version/status, interrupt status/enable/mask, port control, RX WQ/CQ base and size, TX WQ/CI/PI, MAC filters, filter pass/discard counters, RX DMA, TX status, register dump size, PLU TX/RX SGMII fields, IPG sizes, pause counter offsets, and LLU counter-enable bits. Version-specific macros select BF2 or BF3 pause counter offsets through `priv->hw_version`.

## Control Flow and State
The header has no runtime flow, but its constants drive every MMIO state transition in the driver: open/stop clean-port, interrupt enable/clear, RX/TX ring setup, MAC filtering/promiscuous mode, stats reads, pause stats, and BF3 link-speed updates.

## Dependencies and Integration Points
It includes bitfield helpers and is included by all BlueField GigE implementation files. It also defines `MLXBF_GIGE_MMIO_REG_SZ` for ethtool register dumps.

## Risks and Test Signals
Risks include stale offsets for BF2/BF3 revisions, macro expressions depending on a local variable named `priv`, incorrect register dump sizing, and missed masks for error/status bits. Test signals are successful open/close, interrupt clearing, RX/TX traffic, ethtool register dumps, BF3 speed change programming, pause counter reads on both hardware versions, and hardware documentation cross-checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_rx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_rx.c

## Purpose
`mlxbf_gige_rx.c` implements BlueField GigE receive setup, MAC filtering, promiscuous/multicast mode, RX descriptor teardown, packet completion processing, and NAPI polling.

## Important APIs, Types, and Functions
Public helpers include `mlxbf_gige_enable_multicast_rx()`, `mlxbf_gige_disable_multicast_rx()`, MAC filter enable/disable/set/get helpers, `mlxbf_gige_enable_promisc()`, `mlxbf_gige_disable_promisc()`, `mlxbf_gige_rx_init()`, `mlxbf_gige_rx_deinit()`, and `mlxbf_gige_poll()`. The main packet function is local `mlxbf_gige_rx_packet()`.

## Control Flow and State
RX init programs the broadcast filter, allocates coherent RX WQE memory, allocates and DMA-maps one aligned SKB per ring entry, writes the RX WQ base, allocates coherent CQE memory, initializes CQE valid bits, writes CQ base and producer index, enables CRC stripping and filter counters, programs queue size, unmasks RX interrupts, and enables RX DMA. Packet processing reads hardware RX PI, checks the CQE valid bit against `priv->valid_polarity`, handles good packets by allocating a replacement SKB before unmapping and delivering the old SKB, updates stats on MAC/truncation errors, writes the replenished PI after a barrier, flips polarity on ring wrap, and returns whether more packets may remain.

State includes `priv->rx_skb[]`, WQE/CQE coherent memory and DMA addresses, hardware PI/CI registers, `valid_polarity`, netdev stats, and error counters. RX deinit disables DMA, unmaps/frees every SKB, frees WQE/CQE memory, clears base registers, and nulls pointers.

## Dependencies and Integration Points
The file depends on DMA APIs, SKB allocation helper from main, netdev/NAPI APIs, MMIO register definitions, Ethernet protocol classification, and interrupt masking behavior from the hardware RX IRQ path.

## Risks and Test Signals
Risks include replacement SKB allocation failure causing the packet to stay pending, DMA unmap length mismatches, polarity wrap errors, RX PI/CI races, delivering packets before descriptor replacement is visible, and freeing active DMA buffers. Test signals are sustained RX traffic, ring wraparound, RX allocation failure injection, MAC/truncation error counters, multicast/promiscuous filtering, NAPI budget behavior, and open/close leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_tx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_tx.c

## Purpose
`mlxbf_gige_tx.c` implements BlueField GigE transmit ring allocation, completion cleanup, queue availability accounting, WQE pointer advancement, and `ndo_start_xmit`.

## Important APIs, Types, and Functions
Public functions are `mlxbf_gige_tx_init()`, `mlxbf_gige_tx_deinit()`, `mlxbf_gige_handle_tx_complete()`, `mlxbf_gige_update_tx_wqe_next()`, and `mlxbf_gige_start_xmit()`. Local `mlxbf_gige_tx_buffs_avail()` computes ring space under `priv->lock`.

## Control Flow and State
TX init allocates coherent WQE memory, writes its DMA base, allocates a coherent completion counter, writes its DMA base, programs queue size, and resets producer/consumer software indexes. `start_xmit()` linearizes or drops oversized/nonlinear SKBs, enforces the hardware rule that a DMA transfer cannot cross a 4 KB page by copying into an aligned SKB when needed, maps the buffer, writes a two-qword WQE with DMA address and packet length, stores the SKB by producer index under lock, advances `tx_pi`, and rings the hardware producer index unless xmit-more batching is active. If the ring becomes full, it stops the queue and schedules NAPI because there is no separate TX completion interrupt.

Completion reads TX status and hardware consumer index, loops from `prev_tx_ci` to `tx_ci` with 16-bit wrap support, updates stats from WQE packet length, unmaps DMA, consumes SKBs, and wakes the stopped queue if space is available. Deinit frees any outstanding SKBs and coherent resources.

## Dependencies and Integration Points
The file depends on DMA mapping, SKB APIs, netdev queue control, NAPI scheduling, MMIO register definitions, and the aligned SKB allocator in `mlxbf_gige_main.c`.

## Risks and Test Signals
Risks include TX ring full/empty ambiguity, stale `tx_wqe_next`, DMA mapping leaks on copied SKBs, queue stall if NAPI is not scheduled, data corruption if buffers cross 4 KB pages, and concurrency around `tx_pi`/`prev_tx_ci`. Test signals are TX traffic under batching, small frames, oversized SKB drops, fragmented SKB linearization, forced 4 KB crossing packets, ring wrap and full conditions, no-TX-completion-interrupt recovery, and open/close with outstanding packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Kconfig

## Purpose
This Kconfig file defines `CONFIG_MLXFW`, the shared Mellanox firmware flash library used by mlxsw and other Mellanox drivers.

## Important APIs, Types, and Functions
The symbol is a tristate named `MLXFW`; it selects `XZ_DEC` for MFA2 component-block decompression and `NET_DEVLINK` for firmware flash status reporting.

## Control Flow and State
There is no runtime flow. Build-time selection controls whether `mlxfw.o` is built and whether callers can link against `mlxfw_firmware_flash()`. The selected dependencies ensure the parser and devlink notification paths are available.

## Dependencies and Integration Points
`MLXSW_CORE` selects `MLXFW`. The library integrates with firmware blobs, devlink flash update, XZ decompression, and per-device callback implementations supplied through `struct mlxfw_dev_ops`.

## Risks and Test Signals
Risks include missing selected dependencies or making the symbol unavailable to drivers that call the flash API. Test signals are build coverage with `MLXFW=y/m/n`, mlxsw builds, and devlink flash paths resolving `mlxfw_firmware_flash()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Makefile

## Purpose
The mlxfw Makefile links the common Mellanox firmware flash module.

## Important APIs, Types, and Functions
It builds `mlxfw.o` from `mlxfw_fsm.o`, `mlxfw_mfa2_tlv_multi.o`, and `mlxfw_mfa2.o` when `CONFIG_MLXFW` is enabled.

## Control Flow and State
There is no runtime control flow. The object composition combines devlink/FSM flashing logic, MFA2 TLV walking, and MFA2 firmware parsing/decompression.

## Dependencies and Integration Points
The file is controlled by the Kconfig symbol and links code that depends on devlink, firmware blobs, and XZ decompression.

## Risks and Test Signals
Risks are stale object lists or missing parser/FSM objects causing unresolved symbols. Test signals are module and built-in builds, `modinfo mlxfw`, and link checks for `mlxfw_firmware_flash()` and MFA2 helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw.h

## Purpose
`mlxfw.h` is the public in-kernel interface for the Mellanox firmware flash library. It defines the device wrapper, firmware FSM states and errors, reactivation statuses, device operation callbacks, logging helpers, and the `mlxfw_firmware_flash()` entry point.

## Important APIs, Types, and Functions
Important types are `struct mlxfw_dev`, `enum mlxfw_fsm_state`, `enum mlxfw_fsm_state_err`, `enum mlxfw_fsm_reactivate_status`, and `struct mlxfw_dev_ops`. Operations include component query/update, FSM lock/query/cancel/release, block download, component verify, activate, and optional reactivate. `mlxfw_dev_dev()` maps devlink to device for logging.

## Control Flow and State
The header has no direct runtime flow, but it defines the callback contract used by `mlxfw_fsm.c`. If `CONFIG_MLXFW` is not reachable, `mlxfw_firmware_flash()` is an inline `-EOPNOTSUPP` stub. State is caller-owned in `struct mlxfw_dev`: PSID identity, PSID size, devlink pointer, and operations table.

## Dependencies and Integration Points
It depends on Linux firmware, netlink extack, device, and devlink APIs. It is consumed by mlxsw and any device driver that delegates firmware flashing to mlxfw.

## Risks and Test Signals
Risks include callback contract drift, missing operation implementations, wrong PSID length, and callers not handling the stub case. Test signals are build coverage with reachable/unreachable `CONFIG_MLXFW`, devlink flash invocation, callback error propagation, and compile-time use of all enum values by device implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_fsm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_fsm.c

## Purpose
`mlxfw_fsm.c` drives firmware flashing through a device-provided FSM callback interface and devlink status notifications. It validates MFA2 firmware, locks the device FSM, optionally reactivates prior firmware state, downloads each matching component in aligned blocks, verifies components, activates the image, and releases the FSM.

## Important APIs, Types, and Functions
The exported API is `mlxfw_firmware_flash()`. Core helpers are `mlxfw_fsm_state_err()`, `mlxfw_fsm_state_wait()`, `mlxfw_fsm_reactivate_err()`, `mlxfw_fsm_reactivate()`, `mlxfw_status_notify()`, `mlxfw_flash_component()`, and `mlxfw_flash_components()`. It maps FSM error codes to Linux errnos and extack messages.

## Control Flow and State
`mlxfw_firmware_flash()` checks the MFA2 fingerprint, initializes the MFA2 parser, locks the firmware FSM, waits for `LOCKED`, runs optional reactivation, waits again, flashes all components matching the device PSID, activates the image, waits for `LOCKED`, releases the handle, reports completion, and frees parser state. Component flashing queries max size/alignment/write size, starts component update, waits for `DOWNLOAD`, sends aligned chunks through `fsm_block_download()`, verifies the component, and waits back to `LOCKED`. On component download/verify errors it cancels the FSM; top-level errors release the handle.

State is primarily device firmware FSM state addressed by `fwhandle`. Software state includes current component, chunk offset, reactivation support flag, extack messages, and devlink progress notifications. No firmware data is persisted by this file directly; persistence happens inside device callbacks.

## Dependencies and Integration Points
The file depends on mlxfw device callbacks, MFA2 parser APIs, devlink flash status notification, netlink extack, kernel sleep, modules, and XZ-backed component extraction in `mlxfw_mfa2.c`.

## Risks and Test Signals
Risks include timeout waiting for FSM state, bad alignment causing invalid download chunks, incorrect errno/extack mapping, failing to cancel after partial component update, device reset requirements after reactivation, and component count/PSID mismatches. Test signals are devlink flash of valid and invalid MFA2 files, PSID-not-found failure, callback fault injection at every FSM step, timeout tests, chunk alignment boundary tests, reactivation supported/unsupported/status-error cases, and devlink progress notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.c

## Purpose
`mlxfw_mfa2.c` parses Mellanox MFA2 firmware containers. It validates the fingerprint and TLV topology, locates device descriptors by PSID, counts referenced components, decompresses XZ component-block data to a requested offset, checks component magic, and returns component payloads for flashing.

## Important APIs, Types, and Functions
Public functions are `mlxfw_mfa2_check()`, `mlxfw_mfa2_file_init()`, `mlxfw_mfa2_file_component_count()`, `mlxfw_mfa2_file_component_get()`, `mlxfw_mfa2_file_component_put()`, and `mlxfw_mfa2_file_fini()`. Important local helpers validate device and component TLVs, find device/component descriptors, drive XZ decode, and map XZ errors to Linux errors. `struct mlxfw_mfa2_comp_data` owns the returned component and backing buffer.

## Control Flow and State
Initialization checks the fixed fingerprint, finds the first TLV after aligned fingerprint bytes, requires a package descriptor multi-TLV, extracts device/component counts and compressed component-block offset/size, validates component-block bounds, and validates every device and component descriptor. Component count searches for a matching PSID TLV and counts `COMPONENT_PTR` children. Component get follows the selected component pointer to a component descriptor, allocates a buffer for magic plus payload, decompresses the compressed component block up to the requested offset and size, validates `#BIN.COMPONENT!#`, and returns a payload pointer after the magic.

State is read-only firmware data plus parser metadata in `struct mlxfw_mfa2_file`; returned components are vmalloc-backed temporary buffers and must be released with `mlxfw_mfa2_file_component_put()`.

## Dependencies and Integration Points
The file depends on Linux firmware blobs, vmalloc, XZ decompression, netlink alignment, TLV helpers, MFA2 format definitions, and `mlxfw_fsm.c`, which consumes component counts and payloads during devlink flash.

## Risks and Test Signals
Risks include malformed TLV bounds, off-by-one pointer validation, unsupported compression fields not checked beyond XZ expectation, large decompression cost when seeking offsets, integer overflow in component buffer sizing, PSID length mismatches, and accepting invalid component indexes. Test signals are parser unit/fuzz tests with truncated TLVs, wrong fingerprint, missing PSID/component descriptors, corrupt XZ streams, wrong component magic, multiple-device PSID selection, large component offsets, and leak checks for component get/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.h

## Purpose
`mlxfw_mfa2.h` declares the MFA2 parser interface used by the firmware flashing FSM.

## Important APIs, Types, and Functions
It defines `struct mlxfw_mfa2_component` with firmware component index, data size, and data pointer, forward-declares `struct mlxfw_mfa2_file`, and declares check/init/count/get/put/fini functions.

## Control Flow and State
The header has no runtime flow. Its API establishes ownership: `mlxfw_mfa2_file_init()` creates parser state for a firmware blob, component get returns a temporary decompressed component, component put frees it, and file fini releases parser metadata.

## Dependencies and Integration Points
It depends on Linux firmware and `mlxfw.h`. It is included by `mlxfw_fsm.c` and implemented by `mlxfw_mfa2.c`.

## Risks and Test Signals
Risks include prototype drift, unclear ownership causing leaks, and component data being used after `component_put()`. Test signals are build coverage and flash tests that get and put every component along successful and failing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_file.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_file.h

## Purpose
`mlxfw_mfa2_file.h` defines the internal parsed MFA2 file state and a pointer-bounds helper.

## Important APIs, Types, and Functions
`struct mlxfw_mfa2_file` stores the source firmware pointer, first device TLV, device count, first component TLV, component count, compressed component-block pointer, and compressed component-block size. `mlxfw_mfa2_valid_ptr()` checks that a pointer lies strictly inside the firmware byte range.

## Control Flow and State
There is no top-level runtime flow, but the inline pointer validation is used before interpreting TLV headers, payloads, and component-block bounds. The structure is read-only after parser initialization except for normal lifetime management.

## Dependencies and Integration Points
It depends on Linux firmware and kernel types. It is used by TLV accessors, multi-TLV walkers, and the MFA2 parser.

## Risks and Test Signals
Risks include strict pointer checks rejecting boundary-valid zero-length constructs or allowing arithmetic overflow before validation. Test signals are malformed/truncated firmware parser tests, KASAN/UBSAN coverage around pointer arithmetic, and successful parsing of known-good MFA2 images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_format.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_format.h

## Purpose
`mlxfw_mfa2_format.h` defines the on-file MFA2 TLV type IDs and packed payload layouts used by the parser.

## Important APIs, Types, and Functions
It declares TLV type enum values for multi-part, package descriptor, component descriptor, component pointer, and PSID. It also declares compression type values and packed payload structures: `mlxfw_mfa2_tlv_package_descriptor`, `mlxfw_mfa2_tlv_multi`, `mlxfw_mfa2_tlv_psid`, `mlxfw_mfa2_tlv_component_ptr`, and `mlxfw_mfa2_tlv_component_descriptor`. Macro invocations generate typed TLV payload accessors.

## Control Flow and State
There is no runtime flow. The structures define how parser code reads counts, offsets, compressed block sizes, PSID bytes, component indexes, component identifiers, offsets, and payload sizes from big-endian firmware bytes.

## Dependencies and Integration Points
It depends on `mlxfw_mfa2_file.h` and `mlxfw_mfa2_tlv.h`. It is used by both parser validation and component extraction.

## Risks and Test Signals
Risks include packed layout drift from the MFA2 specification, wrong endianness interpretation by callers, and type IDs not matching generated images. Test signals are parsing real MFA2 files, checking component counts and offsets against vendor tooling, and compile-time layout review for packed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv.h

## Purpose
`mlxfw_mfa2_tlv.h` defines the common MFA2 TLV header and typed payload accessor macros.

## Important APIs, Types, and Functions
`struct mlxfw_mfa2_tlv` contains version, type, big-endian length, and flexible payload. `mlxfw_mfa2_tlv_get()` validates a TLV header pointer. `mlxfw_mfa2_tlv_payload_get()` validates bounds, type, and fixed or variable payload length. `MLXFW_MFA2_TLV()` and `MLXFW_MFA2_TLV_VARSIZE()` generate typed accessor functions.

## Control Flow and State
The inlines implement defensive parsing flow: reject invalid header/payload pointers, reject wrong type, reject fixed-size length mismatch, and reject variable-size payloads shorter than the required structure prefix. They return raw pointers into the immutable firmware blob.

## Dependencies and Integration Points
The file depends on kernel byte-order/types and `mlxfw_mfa2_file.h`. It is included by format definitions, multi-TLV walking, and parser validation.

## Risks and Test Signals
Risks include length fields that exclude or include header size differently than callers assume, pointer arithmetic overflow, and returning unaligned packed payload pointers. Test signals are fuzzed TLV parsing, malformed length/type tests, KASAN/UBSAN, and successful access to every known MFA2 payload type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.c

## Purpose
`mlxfw_mfa2_tlv_multi.c` implements walking and searching helpers for MFA2 multi-TLV containers.

## Important APIs, Types, and Functions
It implements `mlxfw_mfa2_tlv_multi_child()`, `mlxfw_mfa2_tlv_next()`, `mlxfw_mfa2_tlv_advance()`, `mlxfw_mfa2_tlv_multi_child_find()`, and `mlxfw_mfa2_tlv_multi_child_count()`. `MLXFW_MFA2_TLV_TOTAL_SIZE()` computes aligned TLV size from header plus payload length.

## Control Flow and State
The first child starts after the aligned `struct mlxfw_mfa2_tlv_multi` payload. `tlv_next()` skips the current TLV, and if it is a multi-part TLV, also skips its aligned child payload region using `multi->total_len`. `tlv_advance()` repeatedly follows next pointers. Find/count iterate over the generated multi-foreach macro and match child `type` values, returning an indexed child or count.

## Dependencies and Integration Points
The file depends on netlink alignment, TLV payload accessors, MFA2 format types, and parser validation in `mlxfw_mfa2.c`.

## Risks and Test Signals
Risks include off-by-one child counts because the macro iterates `num_extensions + 1`, corrupt `total_len` skipping outside the file, and wrong alignment assumptions. Test signals are parser tests for nested/adjacent multi-TLVs, missing child types, malformed child lengths, multiple component pointers, and bounds-check failures without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.h

## Purpose
`mlxfw_mfa2_tlv_multi.h` declares multi-TLV walking helpers and iteration macros for MFA2 parsing.

## Important APIs, Types, and Functions
It declares child, next, advance, child-find, and child-count functions. `mlxfw_mfa2_tlv_foreach()` walks a fixed number of sibling TLVs from a starting TLV. `mlxfw_mfa2_tlv_multi_foreach()` walks children of a multi-TLV using `num_extensions + 1`.

## Control Flow and State
There is no standalone runtime flow, but the macros create parser loops in validation, device lookup, component lookup, and counting. The macros update caller-provided `tlv` and `idx` variables and depend on `mlxfw_mfa2_tlv_next()` returning `NULL` on malformed input.

## Dependencies and Integration Points
It depends on TLV, format, and file-state headers and is included by both the multi-TLV implementation and MFA2 parser.

## Risks and Test Signals
Risks include callers failing to handle `NULL` TLVs during macro iteration, child-count interpretation mismatches, and macro side effects on variable names. Test signals are build coverage, parser validation of malformed multi-TLVs, and successful component count/find operations for devices with several component pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_tlv_multi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Kconfig

## Purpose
`mlxsw/Kconfig` defines build options for Mellanox switch ASIC support: common core, optional HWMON and thermal support, PCI and I2C bus implementations, Spectrum Ethernet switch support, Spectrum DCB, and a minimal I2C driver.

## Important APIs, Types, and Functions
Symbols are `MLXSW_CORE`, `MLXSW_CORE_HWMON`, `MLXSW_CORE_THERMAL`, `MLXSW_PCI`, `MLXSW_I2C`, `MLXSW_SPECTRUM`, `MLXSW_SPECTRUM_DCB`, and `MLXSW_MINIMAL`. Dependencies select devlink, mlxfw, auxiliary bus, page pool, switchdev, VLAN, optional tunneling/bridge/sample modules, PTP support, and allocator libraries.

## Control Flow and State
There is no runtime flow. The dependency graph controls which buses and feature modules can be built and prevents invalid built-in/module combinations for HWMON. Defaults generally build bus and Spectrum support as modules when dependencies are present.

## Dependencies and Integration Points
The file integrates mlxsw with NET_DEVLINK, MLXFW, PCI, I2C, switchdev, bridge/VLAN/tunnel subsystems, PTP, DCB, HWMON, thermal, generic allocator, PARMAN, OBJAGG, and page pool.

## Risks and Test Signals
Risks include unmet optional dependencies, invalid built-in/module combinations, missing selects for newly used libraries, or enabling Spectrum without required networking subsystems. Test signals are allmodconfig/allyesconfig builds, minimal I2C-only builds, Spectrum with optional DCB/PTP, and module dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Makefile

## Purpose
`mlxsw/Makefile` defines object composition for the Mellanox switch core, bus drivers, Spectrum switch driver, and minimal I2C driver.

## Important APIs, Types, and Functions
It builds `mlxsw_core.o` from core, ACL, environment, and linecard objects plus optional HWMON/thermal objects. It builds `mlxsw_pci.o`, `mlxsw_i2c.o`, `mlxsw_spectrum.o` from a broad list of switchdev/router/ACL/KVDL/MR/qdisc/span/NVE/dpipe/trap/ethtool/policer/PGT/port-range objects, optional DCB and PTP objects, and `mlxsw_minimal.o`.

## Control Flow and State
There is no runtime flow, but link composition defines feature availability inside each module. Optional object additions follow Kconfig symbols, so enabling DCB/PTP pulls corresponding Spectrum objects.

## Dependencies and Integration Points
The Makefile consumes the Kconfig symbols and integrates all mlxsw implementation files with the kernel build system.

## Risks and Test Signals
Risks include omitted source files, stale object names, wrong optional-object guards, and link-order issues for shared symbols. Test signals are module and built-in builds across core-only, PCI/I2C, Spectrum with/without DCB/PTP, and minimal driver configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/cmd.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/cmd.h

## Purpose
`cmd.h` defines the mlxsw firmware command mailbox interface. It provides mailbox allocation helpers, command execution wrappers, opcode/status names, and packed field accessors for firmware, board info, asynchronous queue capabilities, firmware-area mapping, resource queries, switch profile configuration, register access, DQ/CQ/EQ ownership transitions, and queue context programming.

## Important APIs, Types, and Functions
The central API is `mlxsw_cmd_exec()`, wrapped by `mlxsw_cmd_exec_in()`, `mlxsw_cmd_exec_out()`, and `mlxsw_cmd_exec_none()`. Command-specific wrappers include `mlxsw_cmd_query_fw()`, `mlxsw_cmd_boardinfo()`, `mlxsw_cmd_query_aq_cap()`, `mlxsw_cmd_map_fa()`, `mlxsw_cmd_unmap_fa()`, `mlxsw_cmd_query_resources()`, `mlxsw_cmd_config_profile_set()`, `mlxsw_cmd_access_reg()`, SDQ/RDQ `sw2hw`, `hw2sw`, `2err`, query helpers, and CQ/EQ ownership/query helpers. `MLXSW_ITEM*` macros define mailbox fields.

## Control Flow and State
Callers allocate a 4096-byte mailbox, populate fields through generated accessors, and invoke wrappers with opcode, opcode modifier, input modifier, direct-output flag, reset allowance, and mailbox sizes. Firmware commands mutate hardware state: mapping/unmapping firmware pages, configuring switch profiles, transitioning descriptor/completion/event queues between software and hardware ownership, moving queues to error state, and accessing registers. Query commands return firmware revision, board PSID/VSD, AQ capabilities, resources, and queue contexts.

There is no local persistent software state beyond temporary mailboxes, but command results drive core initialization, bus setup, devlink resources, queue allocation, and Spectrum profile selection. The header also encodes firmware ABI details such as resource query limits, VPM entry limits, boardinfo string lengths, flood/LAG/CQE timestamp modes, and CQE versions.

## Dependencies and Integration Points
The file depends on `item.h` generated field helpers, kernel allocation, and `struct mlxsw_core` command transport implemented elsewhere. It is used by mlxsw core, PCI/I2C bus code, queue setup, firmware bootstrap, resource discovery, and Spectrum profile configuration.

## Risks and Test Signals
Risks include opcode/status mismatch, mailbox field offset/width drift, incorrect wrapper opcodes, resource query loop limits, profile fields set without corresponding capability bits, queue state transition misuse, and the `__mlxsw_cmd_query_dq()` wrapper using the `2ERR_DQ` opcode despite comments describing `QUERY_DQ`, which deserves scrutiny against firmware expectations. Test signals are mlxsw probe and firmware bootstrap, PSID read, firmware-area mapping, resource table discovery until end ID, Spectrum profile set, SDQ/RDQ/CQ/EQ create/destroy/query, reset-time access-reg paths, and negative tests for firmware status-to-string reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/cmd.h -->
