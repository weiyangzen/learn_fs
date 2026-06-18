# Research: subset-b-004337

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse.h

Purpose: this header is the shared contract for the Altera Triple-Speed Ethernet MAC driver. It describes the MAC and MDIO register layout, command/status bit definitions, DMA buffer bookkeeping, the SGDMA/MSGDMA operations vtable, per-device private state, and small MMIO accessor helpers used by the main, ethtool, and utility files.

Important APIs, types, and functions: `struct altera_tse_mdio` maps the 32 MDIO registers exposed through the MAC register space. `struct altera_tse_mac` maps the full TSE CSR block, including command configuration, FIFO thresholds, primary/supplemental MAC addresses, statistics counters, hash table, embedded MDIO windows, and 1588 adjustment registers. `struct tse_buffer` carries an skb, DMA address, length, and page-mapping flag. `struct altera_dmaops` abstracts SGDMA and MSGDMA operations such as reset, IRQ enable/disable/clear, TX submission, TX completion count, RX descriptor posting, RX status retrieval, initialization, teardown, and RX start. `struct altera_tse_private` is the central netdev state. Inline helpers `csrrd32()`, `csrrd16()`, `csrrd8()`, `csrwr32()`, `csrwr16()`, and `csrwr8()` perform offset-based MMIO access, and `tse_csroffs()` provides register offsets from `struct altera_tse_mac`.

Control flow: the header itself has no runtime control flow, but its definitions shape every path in `altera_tse_main.c`. Probe fills `struct altera_tse_private`, chooses one `struct altera_dmaops` implementation from OF match data, maps the CSR blocks, and passes the state through NAPI, phylink, IRQ, and netdev callbacks. Data-plane functions use the ring indices and DMA ops fields defined here to move packets. Utility helpers read and modify MAC bits through the inline CSR accessors.

State and persistence: persistent driver state is the lifetime of `struct altera_tse_private`: mapped MAC/DMA/PCS bases, RX and TX ring arrays and indices, IRQ numbers, FIFO depths, descriptor-memory addresses, locks, PHY/MDIO/phylink handles, message level, and selected DMA backend. Hardware state covered by this header includes command configuration bits, FIFO thresholds, statistics counters, multicast hash table, MDIO windows, descriptor memory, and optional PCS access. There is no disk persistence; state is rebuilt on probe/open and discarded on remove/close.

Dependencies and integration points: the header depends on Linux netdevice, PHY, phylink, VLAN, list, bitops, and MMIO conventions. It integrates the Altera MAC with companion SGDMA/MSGDMA headers, `altera_utils`, phylink PCS selection, ethtool setup via `altera_tse_set_ethtool_ops()`, and netdev private data. Register-layout correctness is a hard ABI with the FPGA IP configuration.

Risks: the register struct is used for offset calculations, so padding, ordering, or type changes can break MMIO. The DMA ops table is a cross-file contract; missing or mismatched callbacks can fail only at runtime. Ring counters are unbounded `u32` producer/consumer values with modulo indexing, so code must preserve their arithmetic assumptions. The header advertises hash-filter and supplemental unicast state even though the main driver disables hash filtering during probe.

Test signals: build coverage should catch type and callback signature drift. Runtime signals include successful probe for both SGDMA and MSGDMA compatibles, correct CSR register dumps through ethtool, stable MAC reset/configuration, RX/TX ring operation, MDIO access, phylink mode changes, and no MMIO faults when reading statistics or configuring multicast state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_ethtool.c

Purpose: this file exposes ethtool operations for the Altera TSE netdev. It reports driver/firmware identity, dumps the first 128 MAC registers, exports 31 hardware statistics counters, controls the netdev debug message level, delegates link settings to phylink, and reports timestamping information through the generic helper.

Important APIs, types, and functions: `stat_gstrings` names the ethtool statistics. `tse_get_drvinfo()` reads `megacore_revision` and formats the driver and firmware version. `tse_fill_stats()` reads MAC MIB/RMON counters, including extended 64-bit octet counters assembled from MSB and LSB registers. `tse_get_regs()` returns a versioned 128-register dump. `tse_ethtool_set_link_ksettings()` and `tse_ethtool_get_link_ksettings()` call phylink. `tse_ethtool_ops` wires these callbacks into ethtool, and `altera_tse_set_ethtool_ops()` assigns them to the netdev.

Control flow: probe calls `altera_tse_set_ethtool_ops()` after netdev setup. User ethtool requests enter the relevant callbacks. Statistics and register reads directly sample `priv->mac_dev` through the CSR helpers. Link ksettings are not interpreted locally; they are forwarded to `priv->phylink`, which coordinates with the PHY or PCS.

State and persistence: the only software state modified here is `priv->msg_enable` through get/set message-level callbacks. All statistics are hardware counters in the MAC CSR block and are not cached in the driver. Register dump version is fixed at `1`, documenting the current 128-register layout.

Dependencies and integration points: the file depends on `altera_tse.h`, Linux ethtool, netdevice, PHY, and phylink APIs. It assumes the MAC register block is mapped and powered enough for CSR reads when ethtool calls arrive. It also relies on the main driver to initialize `priv->phylink`.

Risks: statistics are sampled as separate MMIO reads, so extended 64-bit counters can race rollover between MSB and LSB reads. `tse_gstrings()` ignores `stringset` and copies stats strings unconditionally, relying on ethtool to call it only for supported sets. Register dumps expose raw hardware state and can fault or return stale values if called during teardown or while clocks are gated. Link setting behavior depends entirely on phylink setup correctness in the main file.

Test signals: useful checks include `ethtool -i` showing `altera_tse` and a revision, `ethtool -S` returning all 31 named counters, `ethtool -d` returning 512 bytes with version `1`, message-level get/set changing debug output, link ksettings changing through phylink, and clean behavior when the interface is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_main.c

Purpose: this is the platform netdev driver for the Altera Triple-Speed Ethernet MAC. It binds FPGA MAC instances described in device tree, selects SGDMA or MSGDMA support, maps MAC/DMA/PCS resources, creates an optional MDIO bus, integrates phylink and Lynx PCS, manages NAPI RX/TX completion, and implements netdev open, stop, transmit, multicast, MTU, and link callbacks.

Important APIs, types, and functions: module parameters `debug`, `dma_rx_num`, and `dma_tx_num` control logging and ring sizes. MDIO helpers are `altera_tse_mdio_read()`, `altera_tse_mdio_write()`, `altera_tse_mdio_create()`, and `altera_tse_mdio_destroy()`. Buffer helpers include `tse_init_rx_buffer()`, `tse_free_rx_buffer()`, `tse_free_tx_buffer()`, `alloc_init_skbufs()`, `free_skbufs()`, and `tse_rx_refill()`. Data-plane paths are `tse_rx()`, `tse_tx_complete()`, `tse_poll()`, `altera_isr()`, and `tse_start_xmit()`. MAC control paths are `reset_mac()`, `init_mac()`, `tse_set_mac()`, `tse_update_mac_addr()`, multicast helpers, and phylink callbacks `alt_tse_mac_config()`, `alt_tse_mac_link_up()`, and `alt_tse_select_pcs()`. Probe/remove are `altera_tse_probe()` and `altera_tse_remove()`. `altera_dtype_sgdma` and `altera_dtype_msgdma` instantiate the DMA ops vtable for compatible matching.

Control flow: probe allocates an Ethernet netdev, stores private state, selects DMA ops from OF match data, maps descriptor/response resources according to SGDMA or MSGDMA layout, sets DMA masks, maps `control_port`, `rx_csr`, `tx_csr`, and optional `pcs`, configures a PCS regmap, gets RX/TX IRQs and FIFO depths, reads device-tree MAC/MTU/PHY settings, creates the MDIO bus if an `altr,tse-mdio` child exists, initializes netdev features and NAPI, creates a regmap MDIO bus and Lynx PCS, creates phylink with MII/GMII/RGMII/SGMII/1000BASEX support, registers the netdev, and warns on unexpected MAC revisions. Open initializes DMA, resets and initializes the MAC, allocates RX/TX skb rings, requests RX and TX IRQs with the same ISR, enables DMA interrupts, posts all RX descriptors, connects and starts phylink, enables NAPI and the TX queue, starts RX DMA, and enables MAC RX/TX. Interrupts clear DMA IRQ state, disable further DMA IRQs, and schedule NAPI. NAPI completes TX buffers, drains RX status responses into skbs, refills RX descriptors, and reenables interrupts when under budget. TX maps the skb linear head only, submits one DMA buffer through the selected backend, updates producer state and byte stats, and stops the queue near ring exhaustion. Stop reverses phylink, queue, NAPI, IRQ, MAC, DMA, and skb resources.

State and persistence: persistent per-device state lives in `struct altera_tse_private`: mapped MMIO bases, descriptor bus addresses, RX/TX rings, producer/consumer counters, locks, FIFO depths, MDIO/phylink/PCS handles, IRQs, selected DMA ops, and logging level. RX buffers are DMA-mapped while posted to hardware; TX buffers are DMA-mapped until completion. Hardware state includes DMA descriptors, response FIFOs, MAC command/config registers, FIFO thresholds, multicast hash table, statistics, and PCS registers. Nothing is persisted outside runtime; open/close allocate and free packet buffers each time.

Dependencies and integration points: the driver depends on platform devices, device tree resource names (`s1`, `rx_resp`, `tx_desc`, `rx_desc`, `control_port`, `rx_csr`, `tx_csr`, optional `pcs`), named IRQs `rx_irq` and `tx_irq`, properties such as `rx-fifo-depth`, `tx-fifo-depth`, `max-frame-size`, `phy-addr`, and `altr,has-*`, Linux DMA mapping, NAPI, netdevice, OF MDIO, phylink, `mdio-regmap`, `pcs-lynx`, and the SGDMA/MSGDMA companion modules. The file also calls ethtool setup from `altera_tse_ethtool.c` and bit helpers from `altera_utils.c`.

Risks: TX explicitly assumes no scatter/gather support and maps only `skb_headlen()`, while its ring-space check still counts fragments; callers must ensure SG is disabled. `free_skbufs()` frees the TX ring but does not free `rx_ring` after freeing RX buffers, which is worth auditing for leak behavior across open/close cycles. SGDMA descriptor bus addresses are rejected above 32 bits, while MSGDMA allows wider DMA. RX status reading pops response FIFO entries, so `tse_rx()` must process each returned status. MAC reset can fail when PHY clocks are gated and is treated as debug-only in open/stop. Hash-filter support is read then forced off, so multicast behavior falls back to promiscuous-style command bits. Probe mutates the global `altera_tse_netdev_ops.ndo_set_rx_mode`, which could affect all instances. Error unwinding after TX IRQ request failure reuses the same label as phylink connect failure and may not free a successfully requested TX IRQ if later phylink connection fails.

Test signals: validate probe for `altr,tse-1.0`, `ALTR,tse-1.0`, and `altr,tse-msgdma-1.0`; resource-name and IRQ failure paths; DMA mask fallback; MDIO child registration and PHY autodetection; SGMII/1000BASEX PCS selection; open/close cycles under leak checking; RX and TX traffic through both DMA backends; queue stop/wake under ring pressure; VLAN-tag receive path; MTU changes only while down; multicast/promiscuous transitions; ethtool stats/registers; link speed and duplex updates for 10/100/1000; and NAPI interrupt reenable after mixed RX/TX completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.c

Purpose: this file provides four tiny read-modify-write helpers for manipulating bit masks in Altera TSE MMIO registers through the CSR accessors from `altera_tse.h`.

Important APIs, types, and functions: `tse_set_bit()` reads a 32-bit register, ORs a mask, and writes it back. `tse_clear_bit()` reads, clears a mask, and writes back. `tse_bit_is_set()` and `tse_bit_is_clear()` return integer truth values after reading the register. All functions accept a base `void __iomem *`, byte offset, and `u32` mask.

Control flow: callers in the main driver use these helpers around MAC command/config and TX/RX command-status registers. Each helper performs exactly one read and, for setters, one write; there is no locking inside the utility file.

State and persistence: the helpers mutate hardware register state only. They do not hold software state, cache values, or persist information beyond the device register write.

Dependencies and integration points: the file includes `altera_tse.h` for `csrrd32()` and `csrwr32()` and `altera_utils.h` for declarations. It is shared by the MAC reset/configuration and multicast/link code in `altera_tse_main.c`.

Risks: these are non-atomic read-modify-write operations against MMIO. Callers must hold the appropriate driver lock, such as `mac_cfg_lock`, when concurrent updates are possible. Any register with write-one-to-clear or side-effect bits would be unsafe with these generic helpers; current callers use command-style registers where read-modify-write is expected.

Test signals: compile/link checks should verify exported declarations match. Runtime signals are correct setting and clearing of MAC enable, reset, RX shift, TX shift, CRC, and promiscuous bits without losing unrelated command-config fields under concurrent link/multicast changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.h

Purpose: this header declares the Altera TSE register bit helper functions implemented in `altera_utils.c`.

Important APIs, types, and functions: it declares `tse_set_bit()`, `tse_clear_bit()`, `tse_bit_is_set()`, and `tse_bit_is_clear()`, all taking an MMIO base, register offset, and bit mask. The header includes Linux compiler and type definitions so callers can use `void __iomem`, `size_t`, and `u32`.

Control flow: the header has no runtime flow. Including C files call the declared helpers to update MAC and DMA-related registers.

State and persistence: no state is defined here. State changes happen in hardware when the implementation functions are called.

Dependencies and integration points: it is included by `altera_tse_main.c` and `altera_utils.c`. Its include guard is `__ALTERA_UTILS_H__`.

Risks: because the helpers perform unlocked read-modify-write operations, the header contract should remain clear that locking is a caller responsibility. Signature drift would affect every MAC configuration call site.

Test signals: build coverage is sufficient for declaration consistency; runtime tests are the same bit-level MAC reset/configuration/link-mode paths that exercise `altera_utils.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Kconfig

Purpose: this Kconfig file exposes Amazon Ethernet device support and the ENA PCI Ethernet driver to kernel configuration.

Important APIs, types, and functions: `NET_VENDOR_AMAZON` is a vendor menu boolean defaulting to `y`. Inside that menu, `ENA_ETHERNET` is a tristate for Elastic Network Adapter support. The ENA symbol depends on `PCI_MSI`, excludes `CPU_BIG_ENDIAN`, depends on optional PTP clock support through `PTP_1588_CLOCK_OPTIONAL`, and selects `DIMLIB` and `NET_DEVLINK`.

Control flow: the file contributes build-time configuration only. If `NET_VENDOR_AMAZON` is disabled, the ENA question is hidden. If `ENA_ETHERNET` is `m` or `y`, the Amazon Makefile descends into the ENA driver and builds it as a module or built-in object.

State and persistence: persistent state is the kernel `.config` symbol values. There is no runtime state in this file.

Dependencies and integration points: `PCI_MSI` matches ENA's MSI-X interrupt model, `!CPU_BIG_ENDIAN` matches the driver's little-endian descriptor/register assumptions, `PTP_1588_CLOCK_OPTIONAL` supports PHC integration, `DIMLIB` supports adaptive interrupt moderation, and `NET_DEVLINK` supports the devlink companion file.

Risks: the help text contains an extra quote after `Elastic Network Adapter (ENA)`, which is cosmetic. The hard `!CPU_BIG_ENDIAN` dependency prevents unsupported endian builds but also hides the driver from any future big-endian platform work. Missing `PCI` dependency may be covered indirectly by `PCI_MSI`, but config dependency changes should be audited with ENA probe assumptions.

Test signals: configuration tests should verify the ENA option appears only when the vendor menu and dependencies permit it, `CONFIG_ENA_ETHERNET=m` builds `ena.ko`, `=y` links built-in, and disabling `NET_DEVLINK` or `DIMLIB` manually is not possible while ENA is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Makefile

Purpose: this Makefile connects the Amazon Ethernet vendor directory to the ENA subdirectory in Kbuild.

Important APIs, types, and functions: the single rule `obj-$(CONFIG_ENA_ETHERNET) += ena/` includes the `ena` directory when ENA is built-in or modular.

Control flow: there is no runtime behavior. During kernel build, Kbuild descends into `amazon/ena` only when the ENA Kconfig symbol is enabled.

State and persistence: build state is determined solely by `CONFIG_ENA_ETHERNET`.

Dependencies and integration points: it depends on the sibling Kconfig file and the `amazon/ena/Makefile` composite object definition.

Risks: adding another Amazon Ethernet driver would require another conditional subdirectory or object line. A symbol rename in Kconfig without updating this Makefile would silently omit ENA from builds.

Test signals: `make M=drivers/net/ethernet/amazon` with ENA enabled should descend into `ena/`; with ENA disabled it should not build ENA objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/Makefile

Purpose: this Makefile builds the Elastic Network Adapter driver as a composite Kbuild object.

Important APIs, types, and functions: `obj-$(CONFIG_ENA_ETHERNET) += ena.o` declares the final object or module. `ena-y` combines `ena_netdev.o`, `ena_com.o`, `ena_eth_com.o`, `ena_ethtool.o`, `ena_xdp.o`, `ena_phc.o`, `ena_devlink.o`, and `ena_debugfs.o`.

Control flow: Kbuild links the component objects into `ena.o` when ENA is enabled. There is no runtime logic here.

State and persistence: persistent state is the component list and the build mode implied by `CONFIG_ENA_ETHERNET`.

Dependencies and integration points: the object list shows the driver architecture: PCI/netdev front end, communication/admin layer, Ethernet descriptor helpers, ethtool, XDP, PHC, devlink, and debugfs. These objects share headers such as `ena_com.h`, `ena_admin_defs.h`, `ena_eth_io_defs.h`, and `ena_netdev.h`.

Risks: any new translation unit for ENA features must be added here or it will not link. Removing optional-looking files such as `ena_debugfs.o` is not conditional here; the C file handles `CONFIG_DEBUG_FS` internally.

Test signals: module builds should emit one `ena` module containing all listed objects, and missing references between netdev, com, PHC, devlink, and debugfs code should be caught at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_admin_defs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_admin_defs.h

Purpose: this header defines the ENA admin-queue ABI shared between the Linux driver and ENA device firmware. It enumerates admin opcodes, completion statuses, feature IDs, capabilities, queue creation/destruction commands, statistics layouts, RSS/offload/LLQ/PHC feature descriptors, asynchronous event records, and bit masks for packed fields.

Important APIs, types, and functions: key enums include `ena_admin_aq_opcode`, `ena_admin_aq_completion_status`, `ena_admin_aq_feature_id`, `ena_admin_aq_caps_id`, placement policy, link speeds, completion policy, stats type/scope, PHC type/errors, SRD flags, RSS hash function/protocol/fields, OS type, AENQ groups, and notification syndromes. Core command/response structs include `ena_admin_aq_entry`, `ena_admin_acq_entry`, `ena_admin_aq_create_sq_cmd`, `ena_admin_acq_create_sq_resp_desc`, `ena_admin_aq_create_cq_cmd`, `ena_admin_acq_create_cq_resp_desc`, destroy commands, `ena_admin_aq_get_stats_cmd`, `ena_admin_acq_get_stats_resp`, `ena_admin_get_feat_cmd`, `ena_admin_get_feat_resp`, `ena_admin_set_feat_cmd`, and `ena_admin_set_feat_resp`. Feature structs cover device attributes, LLQ, queue limits, MTU, host attributes, interrupt moderation, link config, AENQ config, stateless offloads, RSS hash function/input/indirection, hardware hints, PHC, host info, and customer metrics. The trailing `#define` masks are used with shifts to pack and unpack descriptor fields.

Control flow: the header does not execute code. `ena_com.c` fills these structures, submits them through the admin SQ, waits for ACQ completions, and copies feature/statistics responses into driver state. `ena_devlink.c`, `ena_debugfs.c`, ethtool, PHC, and netdev layers consume the feature and stats data indirectly through `ena_com`.

State and persistence: these structures represent transient command descriptors in DMA-coherent admin queues and persistent device-reported capabilities cached in `struct ena_com_dev`. Host attribute, RSS, customer metric, PHC, and queue descriptors also define DMA memory that remains active after feature setup until teardown.

Dependencies and integration points: the header includes `ena_common_defs.h` for 48-bit memory addresses and depends on Linux bit macros such as `BIT()` and `GENMASK()` from including contexts. It is a strict firmware ABI used by the ENA communication layer and must align with hardware specification versioning.

Risks: packed bitfield comments are implemented as masks and shifts rather than C bitfields, so incorrect masks or shift use can corrupt device commands. Structure layout changes are ABI-sensitive and can break firmware compatibility. Feature IDs are used as bit positions in `supported_features`; adding IDs above current widths requires auditing masks. Some commands use indirect control buffers, so address-width validation in `ena_com_mem_addr_set()` is critical.

Test signals: compile coverage with `ena_com.c` catches names and field availability. Runtime validation includes successful `GET_FEATURE` for device attributes, queue limits, AENQ, offload, LLQ, hardware hints, PHC, RSS features, and link config; successful create/destroy SQ/CQ; correct translation of admin completion statuses; ENI/SRD/customer stats retrieval; AENQ link/keepalive events; and PHC readless timestamp command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_admin_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.c

Purpose: this file is ENA's device communication layer. It owns admin queue initialization and command execution, asynchronous event queue processing, MMIO readless access, device reset/version/DMA-width negotiation, I/O queue creation/destruction, LLQ configuration, feature/statistics commands, RSS resources, host attributes, customer metrics buffers, PHC shared-memory setup and timestamp reads, and interrupt moderation state.

Important APIs, types, and functions: internal state includes `enum ena_cmd_status`, `struct ena_comp_ctx`, and `struct ena_com_stats_ctx`. Admin queue setup uses `ena_com_admin_init_sq()`, `ena_com_admin_init_cq()`, `ena_com_admin_init_aenq()`, `ena_com_init_comp_ctxt()`, `ena_com_submit_admin_cmd()`, `ena_com_handle_admin_completion()`, and `ena_com_wait_and_process_admin_cq()`. Public admin APIs include `ena_com_admin_init()`, `ena_com_admin_destroy()`, `ena_com_execute_admin_command()`, `ena_com_set_admin_running_state()`, `ena_com_set_admin_polling_mode()`, `ena_com_admin_q_comp_intr_handler()`, `ena_com_abort_admin_commands()`, and `ena_com_wait_for_abort_completion()`. Device/feature APIs include `ena_com_validate_version()`, `ena_com_get_dma_width()`, `ena_com_dev_reset()`, `ena_com_get_dev_attr_feat()`, `ena_com_set_aenq_config()`, `ena_com_get_link_params()`, `ena_com_get_eni_stats()`, `ena_com_get_ena_srd_info()`, `ena_com_get_customer_metrics()`, and `ena_com_set_dev_mtu()`. Queue APIs include `ena_com_create_io_queue()`, `ena_com_destroy_io_queue()`, `ena_com_create_io_cq()`, `ena_com_destroy_io_cq()`, and `ena_com_get_io_handlers()`. RSS APIs include `ena_com_rss_init()`, `ena_com_rss_destroy()`, hash function/control setters/getters, and indirection table setters/getters. PHC APIs include `ena_com_phc_supported()`, `ena_com_phc_init()`, `ena_com_phc_config()`, `ena_com_phc_get_timestamp()`, and `ena_com_phc_destroy()`.

Control flow: initialization first sets up MMIO readless response memory, validates version and DMA width, initializes admin SQ/CQ/AENQ rings, writes their DMA bases and capabilities to registers, and marks the admin queue running. Admin command submission takes `q_lock`, verifies running state, captures a completion context, writes the command with phase and command ID, rings the admin doorbell, then waits either by polling or completion interrupt. Completion handling walks ACQ entries by phase bit, copies responses to waiting contexts, updates SQ/CQ heads, and wakes waiters. Device reset writes `DEV_CTL`, waits for reset-in-progress on and off, rewrites the MMIO response address, and updates admin completion timeout from capabilities. Feature discovery reads device attributes first, caches supported feature/capability masks, then reads queue limits, AENQ, offloads, optional hardware hints, optional LLQ, and customer metric support. I/O queue creation initializes host or LLQ submission resources, initializes completion memory, sends create CQ then create SQ admin commands, and stores device queue indexes and MMIO doorbells. AENQ interrupt handling walks phase-owned events, dispatches group handlers, advances head, and rings the AENQ doorbell. RSS setup allocates coherent indirection, hash key, and hash control buffers, then uses feature commands to program device state. PHC config reads PHC feature parameters, registers a coherent response buffer with the device, and timestamp reads serialize through a spinlock, doorbell a request ID, spin until a valid response or expiration, then temporarily block further requests after timeout/error.

State and persistence: `struct ena_com_dev` owns persistent runtime state: admin/AENQ rings, I/O SQ/CQ arrays, BAR mappings, DMA device, netdev pointer, placement policy, queue/header limits, supported features/caps, DMA address width, MMIO readless response buffer, PHC shared memory/statistics, RSS buffers, host attributes, customer metric buffer, interrupt moderation intervals, and LLQ parameters. Admin outstanding command contexts persist while commands are live. Hardware state includes BAR registers for admin/AENQ bases, doorbells, device reset, readless response address, I/O queue creation, AENQ head, and PHC doorbells. All state is runtime only and should be torn down during device removal or reset.

Dependencies and integration points: this file depends on `ena_com.h`, admin definitions, register definitions, Ethernet descriptor definitions, Linux DMA coherent allocation, wait completions, spinlocks, jiffies/time helpers, MMIO accessors, netdevice logging, and devm allocation. It is called by the ENA PCI/netdev layer for probe, reset, queue setup, feature discovery, ethtool/RSS operations, PHC, and stats. Devlink PHC validation and debugfs PHC counters consume state initialized here.

Risks: admin queue correctness depends on phase-bit ring arithmetic, command ID reuse, `outstanding_cmds`, and completion-context lifetime. Timeouts set `running_state=false`, which cascades future admin commands to `-ENODEV`. Readless MMIO uses a single locked shared response and busy-waits up to the configured timeout. DMA address validation depends on `ena_dev->dma_addr_bits` being initialized before commands with memory addresses. LLQ fallback logic must match device capabilities, entry sizes must be 8-byte aligned for `__iowrite64_copy()`, and max TX burst enforcement interacts with Ethernet TX descriptor submission. PHC timestamp reads spin under a lock until expiration and can return `-EBUSY` during block periods. `ena_com_fill_hash_ctrl()` logs unsupported fields but still programs and returns success if `ena_com_set_hash_ctrl()` succeeds, which is a behavioral risk. Queue teardown ignores `-ENODEV` destroy errors but must still free coherent memory. Customer metrics require both capability and a preallocated buffer size.

Test signals: validate admin init against ready/not-ready devices, version rejection below minimum controller version, DMA width boundaries, readless MMIO timeout fallback, admin command success and each completion error mapping, interrupt and polling completion modes, command abort during reset, create/destroy TX/RX queues in host and LLQ placement, LLQ fallback configurations, AENQ group dispatch and doorbell updates, reset timeout handling, feature discovery with and without optional LLQ/hints/PHC/RSS/customer metrics, RSS hash and indirection programming, MTU setting, ENI/SRD/customer stats retrieval, PHC active/error/timeout/block behavior, interrupt moderation resolution changes, and leak-free teardown after partial initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.h

Purpose: this header is the public interface and state definition for ENA's communication layer. It defines queue limits, data structures for admin/AENQ/I/O queues, LLQ, RSS, PHC, host attributes, customer metrics, interrupt moderation, and declares the APIs implemented in `ena_com.c` and used by netdev, ethtool, PHC, devlink, and debugfs code.

Important APIs, types, and functions: major structs include `ena_llq_configurations`, `ena_com_buf`, `ena_com_rx_buf_info`, `ena_com_tx_meta`, `ena_com_llq_info`, `ena_com_io_cq`, `ena_com_io_sq`, `ena_com_admin_queue`, `ena_com_aenq`, `ena_com_mmio_read`, `ena_com_phc_info`, `ena_rss`, `ena_customer_metrics`, `ena_host_attribute`, `ena_com_dev`, `ena_com_dev_get_features_ctx`, `ena_com_create_io_ctx`, and `ena_aenq_handlers`. It declares admin/device APIs, queue create/destroy/access APIs, RSS/hash/indirection APIs, host/debug/customer metric allocation APIs, PHC APIs, interrupt moderation APIs, and `ena_com_config_dev_mode()`. Inline helpers map I/O queues back to `ena_com_dev`, toggle adaptive moderation, query capabilities and customer metrics, compose interrupt registers, and fetch LLQ bounce buffers.

Control flow: the header has no standalone execution, but defines call sequencing expected by the driver: initialize MMIO read request support, initialize admin queues, validate version and features, allocate host/RSS/PHC/customer resources, create I/O queues, use Ethernet descriptor helpers for traffic, process admin/AENQ interrupts, and destroy resources during reset/remove. Inline `ena_com_update_intr_reg()` is used at runtime to prepare interrupt unmask/coalescing writes.

State and persistence: `struct ena_com_dev` is the persistent runtime object for one PCI function. Queue arrays support up to 128 TX/RX queue pairs represented as `ENA_TOTAL_NUM_QUEUES`. PHC stats and request state, RSS tables/keys, customer metrics support and buffer, host debug/info buffers, admin stats, LLQ cached metadata, and interrupt moderation intervals persist until explicit destroy or device reset.

Dependencies and integration points: the header includes Linux DMA, MMIO, wait, spinlock, netdevice, prefetch, and scheduling types plus ENA common/admin/Ethernet/register definition headers. It is central to integration with `ena_com.c`, `ena_eth_com.c`, `ena_netdev`, `ena_ethtool`, `ena_xdp`, `ena_phc`, `ena_devlink`, and `ena_debugfs`.

Risks: the arrays and queue IDs assume `ENA_TOTAL_NUM_QUEUES` bounds everywhere; invalid qids can corrupt adjacent queue state. Inline `container_of()` helpers rely on `io_sq->qid` and `io_cq->qid` matching the array index. LLQ bounce-buffer count must be a power of two for mask arithmetic. Capability checks use `BIT(cap_id)` against a `u32`, so capability enum growth needs auditing. PHC state exposes counters read by debugfs without additional locking.

Test signals: compile/link coverage across all ENA objects is important because this header is broad. Runtime signals include successful admin initialization, queue handler lookup, interrupt register programming, adaptive moderation toggles through ethtool, capability/customer metric queries, LLQ bounce-buffer cycling, PHC support/configuration, and correct behavior with maximum queue counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_common_defs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_common_defs.h

Purpose: this small ABI header defines the common ENA specification version and the device memory-address representation shared by admin and data-path descriptors.

Important APIs, types, and functions: `ENA_COMMON_SPEC_VERSION_MAJOR` is `2` and `ENA_COMMON_SPEC_VERSION_MINOR` is `0`. `struct ena_common_mem_addr` stores a 48-bit physical address as `mem_addr_low`, `mem_addr_high`, and a reserved 16-bit field that must be zero.

Control flow: there is no runtime control flow. `ena_com.c` fills `struct ena_common_mem_addr` through `ena_com_mem_addr_set()` before sending admin commands with DMA addresses.

State and persistence: the struct appears in transient admin command descriptors and persistent device configuration for queues, host attributes, RSS buffers, PHC output, and control buffers. The header itself has no mutable state.

Dependencies and integration points: it is included by `ena_admin_defs.h` and `ena_com.h`. The ENA communication layer validates addresses against the negotiated DMA width before populating this ABI type.

Risks: ENA operates with 48-bit addresses, so callers must not pass addresses wider than device support. The reserved field must remain zero for firmware compatibility. Changing the version constants affects host-info reporting in `ena_com_allocate_host_info()`.

Test signals: feature setup involving host attributes, queue creation, RSS, customer metrics, PHC, and indirect control buffers validates address encoding. DMA width boundary tests should reject unsupported high addresses before commands reach firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_common_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.c

Purpose: this optional file creates ENA debugfs entries when `CONFIG_DEBUG_FS` is enabled. It currently exposes PHC statistics for a netdev under a debugfs directory named after the PCI device.

Important APIs, types, and functions: `phc_stats_show()` prints PHC counters from `adapter->ena_dev->phc.stats` if PHC is active. `DEFINE_SHOW_ATTRIBUTE(phc_stats)` creates file operations. `ena_debugfs_init()` creates the per-device directory and `phc_stats` file. `ena_debugfs_terminate()` removes the directory recursively.

Control flow: the netdev layer calls init during adapter setup and terminate during teardown. Reading `phc_stats` enters the seq-file show callback, checks `ena_phc_is_active()`, and prints `phc_cnt`, `phc_exp`, `phc_skp`, `phc_err_dv`, and `phc_err_ts`.

State and persistence: debugfs state is `adapter->debugfs_base`, which points to the created directory. The displayed counters live in `ena_com_phc_info.stats` and persist for the adapter lifetime. Debugfs files are runtime-only and disappear on teardown or unmount.

Dependencies and integration points: the file is compiled into `ena.o` but only emits code under `CONFIG_DEBUG_FS`. It depends on Linux debugfs/seq_file/Pci headers, `ena_debugfs.h`, `ena_netdev.h`, and PHC helpers from `ena_phc.h`.

Risks: `debugfs_create_dir()` and `debugfs_create_file()` errors are not checked, which is conventional for debugfs but means missing entries may be silent. Counter reads are not locked, so values are best-effort snapshots. If terminate is skipped, debugfs dentries could outlive adapter state; the recursive remove path should be paired with all teardown paths.

Test signals: with debugfs enabled and PHC active, `/sys/kernel/debug/<pci-dev>/phc_stats` should show all five counters. With PHC inactive, the file should read empty. Repeated probe/remove or devlink reload should create and remove entries without stale dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.h

Purpose: this header declares ENA debugfs lifecycle hooks and provides no-op stubs when debugfs support is disabled.

Important APIs, types, and functions: under `CONFIG_DEBUG_FS`, it declares `ena_debugfs_init(struct net_device *dev)` and `ena_debugfs_terminate(struct net_device *dev)`. Otherwise it defines empty static inline versions with the same signatures.

Control flow: including code can call the lifecycle hooks unconditionally. Compile-time configuration chooses real debugfs behavior or no-op behavior.

State and persistence: the header defines no state. Real state is `adapter->debugfs_base` in the netdev private structure when debugfs is enabled.

Dependencies and integration points: it includes Linux debugfs and netdevice headers plus `ena_netdev.h`, tying the hooks to ENA adapter state. It is used by the ENA netdev setup/teardown code.

Risks: because the disabled stubs silently do nothing, tests for debugfs entries must account for kernel configuration. The header includes `ena_netdev.h`, so include-order or dependency cycles need care.

Test signals: both `CONFIG_DEBUG_FS=y` and disabled builds should compile. Runtime debugfs tests should only expect entries in enabled builds; disabled builds should still probe and remove ENA devices normally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.c

Purpose: this file adds devlink support for ENA. It exposes the generic `enable_phc` driver-init parameter, validates PHC support, manages a physical devlink port, and implements driver reinitialization through devlink reload.

Important APIs, types, and functions: `ena_devlink_enable_phc_validate()` rejects enabling PHC on devices without PHC support. `ena_devlink_params` registers `DEVLINK_PARAM_GENERIC_ID_ENABLE_PHC` in driver-init mode. `ena_devlink_params_get()` reads the driver-init value and calls `ena_phc_enable()`. `ena_devlink_disable_phc_param()` forces the parameter false under devlink lock. `ena_devlink_port_register()` and `ena_devlink_port_unregister()` manage a physical devlink port. `ena_devlink_reload_down()` destroys the ENA device under RTNL after rejecting namespace changes. `ena_devlink_reload_up()` restores the device if not already running and reports `DRIVER_REINIT`. Public lifecycle functions allocate, free, register, and unregister the devlink instance.

Control flow: allocation creates a devlink with `ena_devlink_ops`, stores the `ena_adapter *` in devlink private storage, and registers parameters with the current PHC enabled value. Register acquires the devlink lock, registers the port, then registers devlink. Reload down unregisters the port and calls `ena_destroy_device(adapter, false)` under RTNL. Reload up calls `ena_restore_device()` under RTNL if `ENA_FLAG_DEVICE_RUNNING` is clear, then registers the port and reports the performed action on success. Unregister and free reverse registration and parameter setup.

State and persistence: devlink private data stores the adapter pointer. Runtime state includes `adapter->devlink`, `adapter->devlink_port`, and the driver-init `enable_phc` parameter value. The parameter is not a firmware-persistent value; it affects subsequent driver initialization and PHC activation.

Dependencies and integration points: the file depends on net/devlink, PCI device context, `ena_netdev.h` via `ena_devlink.h`, and PHC helpers from `ena_phc.h`. It calls core ENA device teardown/restore functions and checks `ENA_FLAG_DEVICE_RUNNING`.

Risks: reload paths interact with asynchronous reset/recovery; `reload_up()` specifically checks whether another path already initialized the device. Port unregister/register order must remain paired or devlink users can see stale ports. `enable_phc` validation depends on feature discovery having populated PHC support. Namespace reload is explicitly unsupported. Failing parameter registration aborts devlink allocation.

Test signals: `devlink dev show` should show the ENA instance after probe, `devlink port show` should expose a physical port, `devlink dev param show` should show `enable_phc`, enabling PHC should fail with `-EOPNOTSUPP` on unsupported devices, devlink reload should destroy and restore the adapter with `DRIVER_REINIT`, namespace reload should fail, and unregister/remove should leave no devlink port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.h

Purpose: this header declares ENA devlink lifecycle and parameter helpers and defines how to retrieve the ENA adapter pointer from devlink private storage.

Important APIs, types, and functions: `ENA_DEVLINK_PRIV(devlink)` casts `devlink_priv()` to a stored `struct ena_adapter *`. Declarations include `ena_devlink_alloc()`, `ena_devlink_free()`, `ena_devlink_register()`, `ena_devlink_unregister()`, `ena_devlink_params_get()`, and `ena_devlink_disable_phc_param()`.

Control flow: the header has no execution. ENA probe/remove and PHC paths call the declared functions to set up devlink, read the PHC parameter, and disable it when needed.

State and persistence: no state is defined here beyond the private-storage convention. The actual state is the devlink object, devlink port, and adapter pointer managed in `ena_devlink.c`.

Dependencies and integration points: it includes `ena_netdev.h` and `<net/devlink.h>`, tying devlink support to the ENA adapter structure and Linux devlink core.

Risks: the private macro assumes devlink was allocated with enough private storage for one adapter pointer; changing allocation size or type would break all users. Include coupling to `ena_netdev.h` can propagate devlink dependencies broadly.

Test signals: build/link tests should catch declaration drift. Runtime signals are successful devlink allocation/registration, parameter access, reload, and clean unregister/free during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.c

Purpose: this file implements ENA Ethernet data-path descriptor preparation and completion parsing. It converts driver TX/RX contexts into ENA hardware descriptors for host queues or low-latency queues, manages LLQ bounce buffers and tail updates, parses RX completion descriptors into packet buffer lists and checksum/hash flags, posts RX buffers, and checks completion queue emptiness.

Important APIs, types, and functions: private helpers include `ena_com_get_next_rx_cdesc()`, `get_sq_desc_regular_queue()`, `get_sq_desc_llq()`, `ena_com_write_bounce_buffer_to_dev()`, `ena_com_write_header_to_bounce()`, `ena_com_close_bounce_buffer()`, `ena_com_sq_update_llq_tail()`, `ena_com_sq_update_tail()`, `ena_com_cdesc_rx_pkt_get()`, `ena_com_create_meta()`, `ena_com_create_and_store_tx_meta_desc()`, and `ena_com_rx_set_flags()`. Public APIs are `ena_com_prepare_tx()`, `ena_com_rx_pkt()`, `ena_com_add_single_rx_desc()`, and `ena_com_cq_empty()`.

Control flow: TX preparation first verifies queue direction, available SQ space, header length, and LLQ push-header requirements. It copies headers into the LLQ bounce buffer when needed, emits a metadata descriptor if metadata changed or caching is disabled, creates one or more TX descriptors for DMA buffers, marks phase/first/last/completion/request-ID/offload fields, advances queue tail with phase flipping on wrap, closes LLQ bounce buffers by copying them to device memory, and returns the number of hardware descriptors consumed. RX packet retrieval walks completion descriptors by phase bit until a descriptor with `LAST` is found, preserving partial packet state if the packet is incomplete. It validates descriptor count and request IDs, copies lengths and request IDs to the caller's RX context, advances the SQ completion head, extracts offset/checksum/hash/protocol flags from the last descriptor, and reports the descriptor count. RX posting creates one single-buffer descriptor with first/last/completion bits, DMA address, length, request ID, and phase, then advances SQ tail. CQ empty checks for an owned RX completion descriptor.

State and persistence: data-path state is held in `struct ena_com_io_sq` and `struct ena_com_io_cq`: tail/head counters, phase bits, queue depth, LLQ current bounce buffer, descriptors-left counters, cached TX metadata, burst limiter, and RX partial-packet completion count/start index. Hardware-visible state is coherent descriptor memory for host queues or device BAR writes for LLQ, completion rings, and doorbell/tail state updated elsewhere by the netdev layer.

Dependencies and integration points: this file depends on `ena_eth_com.h`, which defines TX/RX context helpers and inline queue-space/head updates, plus `ena_com.h` types and `ena_eth_io_defs.h` descriptor masks. It is called by the ENA netdev TX/RX paths after skb DMA mapping and before/after NAPI completion handling. LLQ mode depends on device configuration negotiated by `ena_com_config_dev_mode()`.

Risks: descriptor phase-bit handling and memory barriers are critical; reading descriptor contents before validating phase or writing LLQ memory before `wmb()` can corrupt traffic. LLQ burst limits can return `-ENOSPC` if callers submit too many entries before a doorbell reset. Header length must fit the negotiated LLQ entry, and LLQ requires a push header. TX metadata caching must be invalidated when offload-relevant fields change. RX completion parsing must handle multi-descriptor packets and partial completions across polls; invalid `FIRST` ordering or `req_id` can return hard errors. `ena_com_indirect_table_get()` in the com layer returns the host table, so RX queue indexes programmed here must remain consistent with RSS conversion.

Test signals: validate TX for host queues and LLQ queues, metadata caching enabled/disabled, TSO/checksum offloads, multi-fragment packets, zero-buffer header-only close paths, queue wrap phase flips, LLQ burst exhaustion, RX single and multi-buffer packets, partial RX completions across polls, invalid `req_id` handling, checksum/hash/protocol flag propagation, RX descriptor posting under full queue conditions, and `ena_com_cq_empty()` before and after completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.c -->
