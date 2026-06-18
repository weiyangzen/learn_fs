# Research: subset-b-004508

This grouped report covers Marvell OCTEON endpoint PF and VF network-driver files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.c

## Purpose
This is the primary PCI and netdev implementation for the OCTEON endpoint Physical Function driver. It registers the `octeon_ep` PCI driver, probes supported CN9K/CNXK PF devices, maps BARs through `octep_device_setup()`, initializes firmware control and PF/VF mailbox state, exposes a Linux Ethernet netdev, and owns open/stop, transmit, NAPI, interrupts, SR-IOV enablement, heartbeat monitoring, and remove cleanup.

## Important APIs, Types, And Functions
- PCI/module surface: `octep_pci_id_tbl`, `octep_driver`, `octep_probe()`, `octep_remove()`, `octep_sriov_configure()`, `octep_init_module()`, and `octep_exit_module()`.
- Netdev surface: `octep_netdev_ops` wires `octep_open()`, `octep_stop()`, `octep_start_xmit()`, `octep_get_stats64()`, `octep_tx_timeout()`, `octep_set_mac()`, `octep_change_mtu()`, `octep_set_features()`, `octep_get_vf_config()`, and `octep_set_vf_mac()`.
- Interrupt setup: `octep_alloc_ioq_vectors()`, `octep_enable_msix_range()`, `octep_request_irqs()`, `octep_setup_irqs()`, and `octep_clean_irqs()` allocate per-queue vector context, enable MSI-X, bind non-IOQ interrupt names to hardware-specific handlers, and register IOQ handlers.
- NAPI and queue accounting: `octep_napi_poll()` calls `octep_iq_process_completions()` and `octep_oq_process_rx()`, then `octep_update_pkt()` acknowledges completed Tx/Rx counts before `octep_enable_ioq_irq()` resends interrupts.
- Work items: `octep_tx_timeout_task()` restarts a running netdev under RTNL, `octep_intr_poll_task()` polls non-IOQ interrupts when the interface is down, `octep_ctrl_mbox_task()` drains firmware control messages, and `octep_hb_timeout_task()` closes the netdev after repeated firmware heartbeat misses.

## Control Flow
Probe enables PCI, sets a 64-bit DMA mask, requests BARs, verifies firmware readiness via a vendor extended capability, allocates `alloc_etherdev_mq()`, sets driver data, calls `octep_device_setup()`, sets up PF/VF mailbox structures, queries firmware info, configures netdev features and MTU/MAC limits, and registers the netdev. `octep_device_setup()` maps BAR0/BAR2/BAR4, selects CN93-compatible or CNXK PF hardware ops by device ID, initializes control mailbox support, and starts delayed non-IOQ polling until the interface is opened.

Open resets hardware queues, allocates IQs and OQs, sets up MSI-X and IRQs, sets real queue counts, adds/enables NAPI, advertises admin/rx/link state through control mailbox, enables hardware queues and interrupts, credits all OQs, and turns carrier on if firmware reports link up. Stop reverses the data path: it sets PF link/Rx down, stops carrier and Tx queues, disables interrupts, disables/deletes NAPI, frees IRQs, completes and frees Tx/Rx queue resources, disables/resets hardware queues, and restarts non-IOQ polling.

Transmit pads short frames, selects the queue from `skb_get_queue_mapping()`, maps the linear skb or gather list, fills `octep_tx_desc_hw`, applies checksum/TSO metadata when firmware supports it, advances the ring write index, stops the subqueue if descriptor space is low, and rings the IQ doorbell when batching should flush. DMA mapping failures free the skb and return `NETDEV_TX_OK`, effectively dropping the frame without retry.

## State And Persistence
State is in memory and hardware registers only. `struct octep_device` stores BAR mappings, hardware ops, firmware capabilities, queue arrays, per-queue stats, PF/VF mailbox state, link info, work structs, control mailbox wait lists, heartbeat miss counter, and delayed work flags. Persistent configuration is not written by this file. Hardware-visible state includes ring base/size registers, interrupt masks, queue doorbells, packet counters, mailbox registers, SR-IOV VF enablement, and firmware-maintained link/MAC/MTU/offload state reached through control mailbox commands.

## Dependencies And Integration Points
The file depends on Linux PCI, netdevice, MSI-X, NAPI, DMA mapping, workqueue, rtnl, SR-IOV, and ethtool integration. It delegates ring allocation to `octep_tx.c` and `octep_rx.c`, hardware register programming to `octep_cn9k_pf.c`/`octep_cnxk_pf.c` via `octep_hw_ops`, firmware control to `octep_ctrl_net.*`, VF mailbox servicing to `octep_pfvf_mbox.*`, and ethtool registration to `octep_ethtool.c`.

## Risks And Edge Cases
- IRQ, workqueue, and netdev teardown ordering is critical because interrupt handlers and delayed work dereference `octep_device`.
- Queue indices and packet counters are intentionally lockless and rely on `READ_ONCE()`, `WRITE_ONCE()`, barriers, NAPI serialization, and hardware counter semantics.
- `octep_start_xmit()` drops frames on DMA mapping failure while returning `NETDEV_TX_OK`; monitoring must use driver stats or kernel logs rather than stack retry behavior.
- Probe deferral depends on a vendor-specific firmware-ready capability; missing or late firmware blocks binding.
- SR-IOV disable refuses assigned VFs, and PF-maintained VF MAC policy blocks VF override only after the PF flag is set.
- `octep_device_cleanup()` frees mailbox slots before `octep_delete_pfvf_mbox()`, so changes around mailbox allocation/freeing need careful double-free review.

## Test Signals
Useful signals are successful `pci_register_driver()`, probe logs, `register_netdev()` success, carrier transitions on open/stop, MSI-X allocation count, IRQ request/free logs, NAPI traffic under Tx/Rx load, ethtool feature negotiation, MTU/MAC changes through control mailbox, SR-IOV VF count changes, VF MAC policy behavior, heartbeat-miss device close, and remove/unload with no use-after-free, DMA leak, or stuck workqueue warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.h

## Purpose
This header defines the PF driver's central device model, PCI IDs, queue/interrupt limits, hardware operation vector, mailbox structures, link-state representation, CSR access helpers, and exported internal APIs used by PF source files.

## Important APIs, Types, And Functions
- Device IDs and limits: `OCTEP_PCI_DEVICE_ID_*`, `OCTEP_MAX_QUEUES`, `OCTEP_MAX_VF`, `OCTEP_MAX_MSIX_VECTORS`, `OCTEP_MMIO_REGIONS`, and interrupt masks such as `OCTEP_INPUT_INTR`, `OCTEP_OUTPUT_INTR`, and `OCTEP_MBOX_INTR`.
- Ring space helpers: `IQ_INSTR_PENDING()` and `IQ_INSTR_SPACE()` compute Tx queue occupancy from write and flush indices.
- Hardware abstraction: `struct octep_hw_ops` provides chip-specific hooks for IQ/OQ/mbox register setup, non-IOQ interrupt classes, IOQ interrupt handling, reset/reinit, queue enable/disable, interrupt enable/disable, polling, and register dumps.
- Main state: `struct octep_device` aggregates config, PCI/netdev pointers, BAR mappings, queues, stats, link info, PF/VF mailbox state, control mailbox state, delayed work, and heartbeat state.
- CSR helpers: `octep_write_csr*()`, `octep_read_csr*()`, `OCTEP_PCI_WIN_READ()`, and `OCTEP_PCI_WIN_WRITE()` access direct and windowed hardware registers.

## Control Flow
The header enables source files to treat `struct octep_device` as the context passed from PCI probe to netdev operations, IRQ handlers, workqueue callbacks, and queue helpers. Chip-specific setup fills `octep_hw_ops`; generic PF code calls those function pointers without hard-coding CN9K/CNXK register layouts. Queue helpers receive `struct octep_iq` and `struct octep_oq` pointers stored in `octep_device`, while control and PF/VF mailbox paths reuse the same device-level firmware and VF state.

## State And Persistence
All fields are runtime state. The header defines no persistent storage. Important mutable state includes `caps_enabled`, `caps_supported`, `mac_addr`, `num_iqs`, `num_oqs`, queue pointer arrays, per-queue stats, `link_info`, `vf_info`, `poll_non_ioq_intr`, `hb_miss_cnt`, and control mailbox wait queues/lists. Register writes through the helpers persist only in device hardware until reset or reprogramming.

## Dependencies And Integration Points
It includes `octep_tx.h`, `octep_rx.h`, and `octep_ctrl_mbox.h`, binding the PF main context to Tx/Rx queue formats and control mailbox protocol. It exposes prototypes for `octep_device_setup()`, queue setup/free/processing functions, CN93/CNXK setup functions, and ethtool setup. Source users depend on Linux netdevice, PCI, DMA, workqueue, waitqueue, and MMIO types through included kernel headers.

## Risks And Edge Cases
- `IQ_INSTR_PENDING()` uses masked subtraction, so queue sizes are expected to be powers of two.
- The register access macros assume BAR0 is mapped and valid; callers must not use them after cleanup.
- `struct octep_hw_ops` must be fully populated for the selected chip before open/IRQ paths run.
- Mailbox and control mailbox fields are shared across interrupt and workqueue paths; lifetime must be synchronized by callers.
- `OCTEP_PCI_WIN_READ()` and `OCTEP_PCI_WIN_WRITE()` perform indirect CSR access without explicit locking in the helper, so concurrent callers need external ordering if the window registers are shared.

## Test Signals
Build coverage should catch missing prototypes or incomplete type dependencies. Runtime signals include successful chip setup populating hardware ops, valid queue counts within `OCTEP_MAX_*`, correct CSR reads/writes during register setup, working indirect PCI window reads, and stable link/VF/control-mailbox behavior across open, stop, SR-IOV, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.c

## Purpose
This file implements the PF side of the PF/VF mailbox protocol. It services VF requests for mailbox version negotiation, link status, Rx/link state, MTU, MAC address, firmware info, offload configuration, bulk link/stats reads, and VF removal, and it forwards PF-originated notifications such as link-status changes to VFs.

## Important APIs, Types, And Functions
- Version gating: `pfvf_cmd_versions[]` maps opcodes to the minimum mailbox version and `octep_pfvf_validate_version()` negotiates the effective version per VF.
- Command handlers: `octep_pfvf_set_mtu()`, `octep_pfvf_get_mtu()`, `octep_pfvf_set_mac_addr()`, `octep_pfvf_get_mac_addr()`, `octep_pfvf_set_rx_state()`, `octep_pfvf_set_link_status()`, `octep_pfvf_get_link_status()`, `octep_pfvf_get_fw_info()`, `octep_pfvf_set_offloads()`, and `octep_pfvf_dev_remove()`.
- Bulk reads: `octep_pfvf_pf_get_data()` stages `octep_iface_link_info` or combined Rx/Tx stats into `mbox->config_data` and returns six-byte fragments on follow-up reads.
- Lifecycle: `octep_setup_pfvf_mbox()` allocates one mailbox object per active VF at the VF's first ring, initializes work, mutexes, register pointers, and VF info; `octep_delete_pfvf_mbox()` cancels and frees those mailboxes.
- Work entry: `octep_pfvf_mbox_work()` reads the VF command register, dispatches by opcode, and writes the response word back.

## Control Flow
PF setup uses active VF count and rings-per-VF from configuration, allocates `struct octep_mbox` at `vf_id * rings_per_vf`, and asks chip-specific `setup_mbox_regs()` to bind PF-to-VF and VF-to-PF data registers. A hardware mailbox interrupt schedules `octep_pfvf_mbox_work()`. The worker serializes the mailbox with `mbox->lock`, reads the command from `vf_pf_data_reg`, handles it, and writes the response to the same VF/PF data register.

Most command handlers proxy the VF request to firmware through `octep_ctrl_net_*()` APIs with the VF ID. MAC handling has extra PF policy: if PF has administratively set the VF MAC, VF attempts to set its own MAC are NACKed and GET returns the PF-maintained address. Bulk link-info and stats reads start with an ACK carrying total byte length, then VF issues fragment requests and PF copies up to `OCTEP_PFVF_MBOX_MAX_DATA_SIZE` bytes per response.

Notifications flow in the opposite direction. `octep_pfvf_notify()` decodes firmware-to-host control mailbox messages, builds a PF/VF mailbox notification word, checks negotiated VF mailbox version in `octep_send_notification()`, and writes the notification to the PF-to-VF data register under the mailbox mutex.

## State And Persistence
Runtime state lives in `oct->mbox[]`, `oct->vf_info[]`, and each mailbox's fragment buffer fields: `config_data_index`, `message_len`, and `config_data`. `vf_info[vf_id].mbox_version` stores negotiation result; `vf_info[vf_id].mac_addr` and flags store PF-managed VF MAC policy. No disk persistence exists. Firmware state may be changed through control mailbox calls for link, Rx, MTU, MAC, remove, and offloads.

## Dependencies And Integration Points
The file depends on `octep_main.h` for device and mailbox structures, `octep_pfvf_mbox.h` for protocol layout, and `octep_ctrl_net.h` for firmware commands. It is integrated with chip-specific interrupt handlers that schedule mailbox work, PF netdev SR-IOV code that sets active VFs, and control mailbox notification delivery from firmware.

## Risks And Edge Cases
- The mailbox protocol fits responses into one 64-bit word, so bulk data fragmentation must maintain index and length accurately.
- Version gating is only applied to PF-originated notifications in this file; command dispatch assumes VF behavior is compatible after negotiation.
- `MAX_VF_PF_MBOX_DATA_SIZE` must cover the largest staged link/stats payload; mismatches can overflow or truncate if structures grow.
- Setup allocates only active VFs present at setup time. If active VFs change after probe, mailbox allocation policy must stay consistent with SR-IOV enable flow.
- Teardown must cancel pending work before freeing mailbox memory.

## Test Signals
Test by loading PF with SR-IOV enabled, probing VFs, validating mailbox version negotiation, VF MAC/MTU/offload/link operations, PF-administered VF MAC rejection, bulk `GET_LINK_INFO` and `GET_STATS` responses over multiple fragments, PF link-status notification delivery, VF remove notification to firmware, and clean unload while mailbox work may be pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.h

## Purpose
This header defines the PF/VF mailbox protocol shared by the PF implementation: protocol versions, opcodes, response types, status constants, link enums, mailbox timing/fragment constants, and the packed 64-bit command/response word format.

## Important APIs, Types, And Functions
- Versions: `enum octep_pfvf_mbox_version` and `OCTEP_PFVF_MBOX_VERSION_CURRENT`.
- Opcodes: `enum octep_pfvf_mbox_opcode` covers version, MTU, MAC, link info, stats, Rx/link state, link status, device remove, firmware info, offloads, and link notification.
- Word types and status: `OCTEP_PFVF_MBOX_TYPE_CMD`, `RSP_ACK`, `RSP_NACK`, plus timeout/NACK/busy status codes.
- Protocol payload: `union octep_pfvf_mbox_word` overlays one `u64` with typed bitfield views for generic data, fragments, version, MAC, MTU, link state/status, firmware info, and offloads.
- Exported PF functions: `octep_pfvf_mbox_work()`, `octep_setup_pfvf_mbox()`, `octep_delete_pfvf_mbox()`, and `octep_pfvf_notify()`.

## Control Flow
The union layout allows a VF to write a single 64-bit command word and the PF to overwrite the mailbox data register with a single 64-bit response. Bulk commands use `s_data.frag` to distinguish the initial length request from subsequent six-byte fragment reads. The PF code uses opcode-specific union members to avoid separate serialization buffers for small commands.

## State And Persistence
The header itself defines no storage. It constrains runtime state in mailbox users by limiting inline payload data to 48 bits or six bytes, setting maximum retries/timeouts, and defining the current protocol version. Protocol version negotiation is persisted only in memory inside PF/VF device structures.

## Dependencies And Integration Points
The protocol is consumed by `octep_pfvf_mbox.c` on the PF side and mirrored in the VF mailbox header. It depends on Linux bit macros and Ethernet lengths through including source context. Firmware-related commands are bridged by PF control mailbox code, while notification opcodes are generated from firmware-to-host control messages.

## Risks And Edge Cases
- Bitfield packing and endianness must match PF and VF builds; the `__packed` union is a hardware/protocol ABI.
- The PF and VF headers duplicate protocol definitions; drift between them can break negotiation and command decoding.
- `OCTEP_PFVF_MBOX_MAX_DATA_SIZE` is six bytes because opcode/type/fragment fields consume the remaining bits; callers must not copy larger inline payloads.
- MTU constants represent hardware frame sizes, not netdev MTU directly.

## Test Signals
Compile both PF and VF users, compare enum/opcode values across PF and VF protocol headers, run version negotiation, exercise each opcode with ACK/NACK paths, and validate multi-fragment data transfers where payload lengths are not multiples of six.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cn9k_pf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cn9k_pf.h

## Purpose
This header maps CN9K/CN93 PF hardware registers and bit definitions used by the OCTEON endpoint PF chip-specific implementation. It provides address formulas for reset, PCIe config, ring, mailbox, interrupt, ring mapping, MAC/PF ring control, firmware status, and indirect PCIe configuration space access.

## Important APIs, Types, And Functions
- Register base macros: `CN93_RST_*`, `CN93_SDP_WIN_*`, `CN93_SDP_EPF_RINFO`, `CN93_SDP_R_IN_*`, `CN93_SDP_R_OUT_*`, `CN93_SDP_R_MBOX_*`, and `CN93_SDP_EPF_*_RINT*`.
- Address calculators: `CN93_SDP_R_IN_* (ring)`, `CN93_SDP_R_OUT_* (ring)`, mailbox per-ring macros, interrupt bit-array macros, and ring mapping macros.
- Field helpers: `CN93_SDP_EPF_RINFO_SRN/RPVF/NVFS`, `CN93_SDP_MAC_PF_RING_CTL_*`, `CN98_SDP_MAC_PF_RING_CTL_*`, and interrupt masks such as `CN93_INTR_R_OUT_INT`.
- PCIe config helper: `cn9k_pemx_pfx_csx_pfcfgx()` builds a PEM/PF config-space address using `FIELD_PREP()` and alignment handling; exposed as `CN9K_PEMX_PFX_CSX_PFCFGX`.
- Constants: `CN93_NUM_NON_IOQ_INTR`, firmware status values, VSEC control offset, BAR4 index data, and interrupt-enable bit.

## Control Flow
This header is declarative. Chip-specific PF setup code uses these macros to calculate CSR offsets, then generic access helpers from `octep_main.h` perform MMIO or indirect PCI window reads/writes. Ring setup uses the IN/OUT register macros; mailbox setup uses per-ring PF/VF register macros; interrupt setup and handlers use EPF interrupt status, W1S, W1C, and enable registers.

## State And Persistence
The file defines no in-memory state. Its constants address hardware state that persists until reset or reconfiguration: ring base/size/control, packet counters, interrupt masks/status bits, mailbox data and interrupt flags, SR-IOV ring mapping, and firmware-running status.

## Dependencies And Integration Points
It includes `linux/bitfield.h` and is intended for CN9K PF hardware implementation files such as `octep_cn9k_pf.c`. It integrates with `octep_hw_ops` population and with generic PF logic that needs hardware register programming but should not embed CN9K offsets.

## Risks And Edge Cases
- Address macros are hardware ABI. A wrong offset or field width can corrupt unrelated CSRs.
- Several bit-array interrupt macros for DMA_VF and PP_VF use `((index) + CN93_BIT_ARRAY_OFFSET)` rather than multiplication, which deserves scrutiny against the hardware manual.
- `CN93_SDP_IN_RING_TB_MAP()` references `CN93_SDP_N_RING_TB_MAP_START`, which appears inconsistent with the defined `CN93_SDP_IN_RING_TB_MAP_START`; users may fail to compile if that macro is exercised.
- CN93 and CN98 MAC/PF ring control fields differ, so chip ID checks must select the correct extractor.

## Test Signals
Build chip-specific PF code with all referenced macros enabled, compare register dumps to hardware documentation, validate queue bring-up on CN93/CN98/CNF95N, test mailbox interrupts and non-IOQ interrupt counts, verify SR-IOV ring mapping values, and confirm indirect PCIe VSEC access through the computed PEM/PF config address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cn9k_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cnxk_pf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cnxk_pf.h

## Purpose
This header maps CNXK PF hardware registers and bit definitions for the OCTEON endpoint PF driver. It is the CNXK counterpart to the CN9K register header, with CNXK-specific offsets, field widths, interrupt counts, output queue watermark register, and PCIe VSEC address calculation.

## Important APIs, Types, And Functions
- Register base macros: `CNXK_RST_*`, `CNXK_SDP_WIN_*`, `CNXK_SDP_EPF_RINFO`, ring IN/OUT register starts, mailbox register starts, EPF interrupt registers, ring mapping registers, and MAC/PF ring-control registers.
- Address calculators: `CNXK_SDP_R_IN_* (ring)`, `CNXK_SDP_R_OUT_* (ring)`, `CNXK_SDP_R_OUT_WMARK(ring)`, `CNXK_SDP_R_MBOX_*`, and EPF interrupt bit-array macros.
- Field helpers: `CNXK_SDP_EPF_RINFO_SRN/RPVF/NVFS`, `CNXK_SDP_MAC_PF_RING_CTL_NPFS/SRN/RPPF`, and ring control masks.
- PCIe config macro: `CNXK_PEMX_PFX_CSX_PFCFGX(pem, pf, offset)` constructs an indirect config-space address for CNXK.
- Constants: `CNXK_NUM_NON_IOQ_INTR`, firmware status values, CNXK VSEC control offset, BAR4 index data, and `CNXK_INT_ENA_BIT`.

## Control Flow
The header does not run control flow directly. CNXK PF setup code uses the macros during device setup, queue reset/setup, interrupt enable/disable, mailbox register binding, and register dumps. Generic PF code reaches those operations through `octep_hw_ops`.

## State And Persistence
No in-memory state is declared. The macros address hardware state for reset domains, queue configuration, OQ watermark/backpressure, counters, mailbox data, interrupt status/enables, SR-IOV mapping, and firmware status. Values written by users persist in device registers until hardware reset or subsequent writes.

## Dependencies And Integration Points
This header is consumed by CNXK PF implementation files and integrates with `octep_main.h` CSR helpers. It complements `octep_regs_cn9k_pf.h` and allows the generic PF driver to handle CN10KA/CNF10KA/CNF10KB/CN10KB devices through a different hardware operation vector.

## Risks And Edge Cases
- CNXK field widths differ from CN9K, especially SRN/NVFS extraction; copying CN9K assumptions into CNXK code can misconfigure rings or VFs.
- OQ register layout includes `CNXK_SDP_R_OUT_WMARK`; missing watermark setup can affect backpressure behavior.
- Like the CN9K header, `CNXK_SDP_IN_RING_TB_MAP()` references `CNXK_SDP_N_RING_TB_MAP_START`, which is not defined in this file and should be checked if used.
- DMA_VF and PP_VF interrupt address macros use addition with the bit-array offset instead of multiplication; confirm against spec.

## Test Signals
Validate CNXK PF probe, queue register programming, OQ watermark programming, MSI-X/non-IOQ interrupt count of 32, mailbox interrupt routing, SR-IOV VF ring mapping, firmware status reads, register dump sanity, and compile coverage for all macros used by CNXK PF code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cnxk_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.c

## Purpose
This file implements PF receive queue allocation, hardware descriptor provisioning, page-buffer refill, packet completion processing, skb construction, checksum status propagation, and receive queue cleanup for OCTEON Output Queues.

## Important APIs, Types, And Functions
- Setup/cleanup: `octep_setup_oqs()`, `octep_setup_oq()`, `octep_free_oqs()`, `octep_free_oq()`, and `octep_oq_free_ring_buffers()`.
- Buffer management: `octep_oq_fill_ring_buffers()` allocates and DMA maps one page per descriptor; `octep_oq_refill()` replenishes consumed descriptors once `refill_threshold` is reached.
- Hardware accounting: `octep_oq_dbell_init()` credits all descriptors; `octep_oq_check_hw_for_pkts()` reads packet counters and updates pending packets.
- Packet processing: `__octep_oq_process_rx()` parses response headers, builds skbs from pages, handles multi-descriptor packets as skb frags, sets checksum state, and submits to GRO; `octep_oq_process_rx()` loops to a NAPI budget and refills descriptors.

## Control Flow
Queue setup allocates `struct octep_oq`, coherent hardware descriptor memory, a software `octep_rx_buffer` array, page buffers for every descriptor, initializes indices, and asks chip-specific `setup_oq_regs()` to write queue registers. During NAPI, `octep_oq_process_rx()` checks whether pending packets are known; if not, it reads hardware counters. It processes up to budget packets, decrementing pending count, and when enough descriptors have been consumed, refills with new pages and writes descriptor credits to hardware.

For each packet, the first page contains an 8-byte hardware response length header and optionally an 8-byte extended offload header. The driver unmaps the page, builds an skb around it, reserves the response header(s), appends either a single buffer or additional page fragments for large packets, sets protocol and checksum status, and calls `napi_gro_receive()`.

## State And Persistence
Runtime OQ state includes descriptor DMA address, `buff_info` pages, `host_read_idx`, `host_refill_idx`, `refill_count`, `last_pkt_count`, `pkts_pending`, `max_single_buffer_size`, `pkts_credit_reg`, `pkts_sent_reg`, and per-queue stats. This state is volatile and tied to open/stop lifetime. Hardware-visible state consists of OQ descriptors, page DMA addresses, packet counter acknowledgements, and descriptor credits.

## Dependencies And Integration Points
The file depends on `octep_config.h` for queue sizes and thresholds, `octep_main.h` for device context and hardware ops, Linux DMA/page allocation APIs, netdevice/NAPI/GRO APIs, and `octep_rx.h` hardware formats. It is called from `octep_open()`, `octep_stop()`, and `octep_napi_poll()`.

## Risks And Edge Cases
- `octep_oq_drop_rx()` receives the original `buff_info` pointer while advancing through fragments; any future change must ensure each consumed fragment page is unmapped and released exactly once.
- Large packets span consecutive descriptors; ring wrap and `data_len` accounting must remain correct.
- Counter wrap handling writes back large packet counters when above `0xF0000000U`; hardware semantics must match this strategy.
- Page allocation or DMA mapping failures reduce refill and packet processing; sustained failures can starve OQ credits.
- Extended response header size is subtracted only when firmware advertises Rx offloads; PF/VF firmware capability mismatches can corrupt packet alignment.

## Test Signals
Run traffic tests for small frames, jumbo frames, fragmented/gathered receive, checksum offload on/off, GRO, NAPI budget exhaustion, descriptor refill threshold behavior, receive under memory pressure, queue stop/start cycles, hardware packet counter wrap simulation if possible, and DMA debug for map/unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.h

## Purpose
This header defines PF receive-side hardware descriptor formats, response headers, offload flags, receive buffer bookkeeping, per-queue/interface statistics, and `struct octep_oq`, the software state for an OCTEON Output Queue.

## Important APIs, Types, And Functions
- Hardware descriptor: `struct octep_oq_desc_hw` contains a DMA buffer pointer and an optional host info pointer; static assert enforces 16 bytes.
- Response headers: `struct octep_oq_resp_hw` stores big-endian packet length; `struct octep_oq_resp_hw_ext` stores Rx offload verification flags.
- Offload helpers: `OCTEP_RX_OFFLOAD_*`, `OCTEP_RX_IP_CSUM()`, `OCTEP_RX_CSUM_IP_VERIFIED`, `OCTEP_RX_CSUM_L4_VERIFIED`, and `OCTEP_RX_CSUM_VERIFIED()`.
- Stats: `struct octep_oq_stats` tracks per-queue packets, bytes, and allocation failures; `struct octep_iface_rx_stats` mirrors hardware interface counters.
- Queue state: `struct octep_oq` stores queue identity, device/netdev pointers, NAPI pointer, buffers, MMIO registers, counters, indices, descriptor memory, and DMA address.

## Control Flow
`octep_rx.c` allocates and fills `octep_oq` instances. Hardware DMA writes packets into pages referenced by `octep_oq_desc_hw`; the driver interprets response headers at the beginning of those pages, updates `octep_oq` indices and counters, and recycles descriptors by writing credits to `pkts_credit_reg`.

## State And Persistence
The header defines runtime-only state structures. `host_read_idx`, `host_refill_idx`, `refill_count`, `pkts_pending`, and `last_pkt_count` are the core receive cursor fields. `iface_rx_stats` fields are snapshots of hardware counters copied elsewhere. No file or firmware-persistent state is defined.

## Dependencies And Integration Points
The types are consumed by PF queue code, PF main NAPI code, ethtool stats, and firmware stats structures. The queue struct embeds Linux `napi_struct` pointers indirectly and depends on DMA address, device, netdev, page, and MMIO pointer types from kernel headers.

## Risks And Edge Cases
- Hardware descriptor and response header sizes are ABI-sensitive; static asserts help catch accidental layout changes.
- Offload verification macros treat either IP or L4 verified flags as enough for `CHECKSUM_UNNECESSARY`; protocol expectations should match firmware semantics.
- `buffer_size` and `max_single_buffer_size` must account for response header sizes exactly to avoid skb length/alignment bugs.
- Queue count and descriptor count assumptions rely on power-of-two ring masks in the main/queue code.

## Test Signals
Build-time static asserts, DMA descriptor programming, checksum-offload receive tests, jumbo receive tests, ethtool/stat consistency, NAPI processing under traffic, and memory-leak checks on open/stop exercise this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.c

## Purpose
This file implements PF transmit queue allocation, descriptor and scatter/gather list management, completion processing, pending-buffer cleanup, and queue teardown for OCTEON Input Queues.

## Important APIs, Types, And Functions
- Setup/cleanup: `octep_setup_iqs()`, `octep_setup_iq()`, `octep_free_iqs()`, `octep_free_iq()`, and `octep_clean_iqs()`.
- Completion: `octep_iq_process_completions()` reads the hardware read index via `hw_ops.update_iq_read_idx()`, unmaps DMA buffers, frees skbs, updates stats, completes BQL accounting, and wakes stopped subqueues.
- Shutdown cleanup: `octep_iq_free_pending()` unmaps and frees all packets between `flush_index` and `host_write_index` and resets BQL state.
- Index management: `octep_iq_reset_indices()` zeros fill, write, read, flush, and hardware completion accounting fields.

## Control Flow
Queue setup allocates a `struct octep_iq`, coherent descriptor ring, coherent per-packet SGL memory, and a software buffer-info array. It precomputes each tx buffer's SGL virtual and DMA address, resets queue indices, and calls chip-specific `setup_iq_regs()`. During NAPI, completion processing updates the device read index, walks descriptors from `flush_index` until the hardware read index or budget, unmaps either single-buffer or gather DMA mappings, frees skbs, advances `flush_index`, updates stats and BQL, and wakes subqueues when descriptor space recovers.

On stop, `octep_clean_iqs()` frees any submitted but not completed buffers and resets indices before hardware queues are disabled/reset and queue structures are freed.

## State And Persistence
Tx state is per-open runtime state: descriptor ring DMA memory, SGL DMA memory, `buff_info`, ring indices, `fill_cnt`, `fill_threshold`, `pkt_in_done`, `pkts_processed`, BQL state, and per-queue stats. No persistent state exists. Hardware-visible state includes the IQ descriptor ring, SGL memory, doorbell writes, and instruction count register acknowledgements.

## Dependencies And Integration Points
The file depends on `octep_tx.h` for formats and stats, `octep_config.h` for queue sizes and thresholds, `octep_main.h` for hardware ops and device context, Linux DMA APIs, skb APIs, and netdev queue/BQL APIs. It is used by `octep_main.c` open/stop and NAPI paths; descriptor contents are prepared by `octep_start_xmit()`.

## Risks And Edge Cases
- DMA unmap logic must mirror mapping logic in `octep_start_xmit()`, including SGL index layout.
- `octep_free_iqs()` assumes queue pointers exist for active ring count; callers must only call it after partial setup cleanup has handled NULLs or active counts are consistent.
- Completion budget returns `!budget`, which signals pending work when budget is exhausted rather than when hardware still has completions.
- Ring size masks require descriptor counts to be powers of two.
- BQL accounting must remain balanced between `netdev_tx_sent_queue()`/`__netdev_tx_sent_queue()` in transmit and `netdev_tx_completed_queue()`/reset in completion/cleanup.

## Test Signals
Exercise Tx under single-buffer and fragmented skb loads, TSO/checksum-enabled traffic, queue-full and wake paths, BQL behavior, open/stop with pending Tx, DMA debug unmap balance, netdev watchdog timeout recovery, and partial allocation failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.h

## Purpose
This header defines PF transmit-side software and hardware formats: scatter/gather descriptors, Tx buffer metadata, interface and queue stats, Input Queue state, instruction header, Tx offload flags, optional metadata, and the 64-byte hardware Tx descriptor.

## Important APIs, Types, And Functions
- SGL format: `struct octep_tx_sglist_desc` stores four 16-bit lengths and four DMA pointers; `OCTEP_SGLIST_ENTRIES_PER_PKT` and `OCTEP_SGLIST_SIZE_PER_PKT` size per-packet SGL storage.
- Buffer bookkeeping: `struct octep_tx_buffer` tracks skb, DMA address, SGL pointers, and gather flag.
- Stats: `struct octep_iface_tx_stats` mirrors hardware interface counters; `struct octep_iq_stats` tracks posted/completed/dropped instructions, bytes, SGL packets, busy events, and restarts.
- Queue state: `struct octep_iq` stores ring indices, descriptor/SGL memory, MMIO registers, netdev queue pointer, fill counts, and stats.
- Hardware descriptor: `struct octep_instr_hdr`, `struct tx_mdata`, and `struct octep_tx_desc_hw`; static asserts enforce descriptor ABI sizes.
- Offload helpers: `OCTEP_TX_OFFLOAD_*`, `OCTEP_TX_IP_CSUM()`, and `OCTEP_TX_TSO()`.

## Control Flow
`octep_main.c` fills `octep_tx_desc_hw` in the transmit path, `octep_tx.c` allocates and frees the rings and consumes completion state, and chip-specific register code binds each `octep_iq` to doorbell, instruction count, and interrupt-level registers. Offload flags are derived from firmware-advertised capabilities and netdev feature settings before descriptors are posted.

## State And Persistence
The structs define runtime-only state. Hardware reads descriptors and SGLs from DMA memory, while software tracks ownership with `host_write_index`, `octep_read_index`, and `flush_index`. Interface stats are copied from hardware elsewhere; per-IQ stats are accumulated in memory.

## Dependencies And Integration Points
The header is included by `octep_main.h`, `octep_tx.c`, PF main transmit logic, and ethtool/stat code. It depends on Linux skb, DMA, netdev queue, and bit macro types through source context. Its descriptor layout is an ABI with OCTEON firmware/hardware.

## Risks And Edge Cases
- Static layout constraints must remain unchanged for hardware compatibility.
- The SGL length order uses reversed length slots relative to pointer index; mapping and unmapping code must agree.
- Offload metadata is byte-swapped before hardware because of ESR behavior; missing or duplicate swapping breaks Tx offloads.
- `u16` ring indices constrain practical descriptor counts and assume mask-based wrap.

## Test Signals
Compile-time static asserts, Tx packet transmission with and without fragments, maximum-fragment skb transmission, TSO and checksum offload validation, completion and BQL stat consistency, and hardware descriptor dump inspection are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Kconfig

## Purpose
This Kconfig entry exposes the Marvell OCTEON PCI Endpoint NIC VF driver as `CONFIG_OCTEON_EP_VF`.

## Important APIs, Types, And Functions
- `config OCTEON_EP_VF` declares a tristate driver option named "Marvell Octeon PCI Endpoint NIC VF Driver".
- Dependencies are `64BIT` and `PCI`.
- Help text identifies the module name as `octeon_ep_vf` and points readers to `Documentation/networking/device_drivers/ethernet/marvell/octeon_ep_vf.rst`.

## Control Flow
Kconfig controls whether the VF driver is omitted, built into the kernel, or built as a module. When enabled, the Makefile builds the object list for `octeon_ep_vf.o`.

## State And Persistence
There is no runtime state here. The selected configuration persists in the kernel build configuration and determines whether the VF driver is compiled.

## Dependencies And Integration Points
The entry integrates with the kernel networking/ethernet driver Kconfig tree. It depends on generic PCI support and a 64-bit build because the driver uses 64-bit DMA and MMIO register accesses.

## Risks And Edge Cases
- Documentation path must exist in the target kernel tree, or help text becomes stale.
- No explicit dependency on the PF driver exists; VFs can be built independently, but runtime operation still requires a compatible PF/firmware mailbox endpoint.
- Missing `PCI_MSI`-style dependency may be acceptable if PCI implies MSI-X availability in the target kernel configuration, but it is worth validating.

## Test Signals
Run Kconfig build matrix checks for `n`, `m`, and `y`, verify the module name, confirm dependency handling on non-PCI or non-64-bit configs, and ensure menu visibility from the parent Marvell Ethernet Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Makefile

## Purpose
This Makefile builds the OCTEON endpoint VF network driver object when `CONFIG_OCTEON_EP_VF` is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_OCTEON_EP_VF) += octeon_ep_vf.o` declares the module/built-in target.
- `octeon_ep_vf-y` lists the constituent objects: `octep_vf_main.o`, `octep_vf_cn9k.o`, `octep_vf_cnxk.o`, `octep_vf_tx.o`, `octep_vf_rx.o`, `octep_vf_mbox.o`, and `octep_vf_ethtool.o`.

## Control Flow
Kbuild links all listed objects into one logical driver object. The file order places `octep_vf_main.o` first, followed by chip-specific setup, queue helpers, mailbox protocol, and ethtool support.

## State And Persistence
There is no runtime state. Build state is produced by Kbuild as object files and, when configured as a module, `octeon_ep_vf.ko`.

## Dependencies And Integration Points
The Makefile integrates the VF directory with the kernel build system. It assumes all listed source files are present and that headers in the same directory provide shared definitions.

## Risks And Edge Cases
- Adding a new source file without updating `octeon_ep_vf-y` leaves code unlinked.
- Removing or renaming any object in the list breaks the build.
- The PF/VF protocol header duplication means build success does not prove runtime compatibility with the PF module.

## Test Signals
Build `CONFIG_OCTEON_EP_VF=m` and `=y`, inspect that `octeon_ep_vf.ko` includes all listed objects, and run modpost for unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cn9k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cn9k.c

## Purpose
This file implements CN9K/CN93-compatible VF hardware operations for queue register setup, reset, interrupt handling, mailbox register binding, queue enable/disable, register dump, and configuration initialization.

## Important APIs, Types, And Functions
- Debug/reset: `cn93_vf_dump_q_regs()`, `cn93_vf_reset_iq()`, `cn93_vf_reset_oq()`, and `octep_vf_reset_io_queues_cn93()`.
- Config: `octep_vf_init_config_cn93_vf()` reads rings-per-VF from `CN93_VF_SDP_R_IN_CONTROL(0)` and initializes descriptor counts, instruction type, thresholds, and MSI-X count.
- Register setup: `octep_vf_setup_iq_regs_cn93()`, `octep_vf_setup_oq_regs_cn93()`, and `octep_vf_setup_mbox_regs_cn93()`.
- Interrupts: `octep_vf_ioq_intr_handler_cn93()` checks for PF-to-VF mailbox status on queue 0, schedules mailbox work, clears mailbox interrupt status, and schedules NAPI.
- Ops registration: `octep_vf_device_setup_cn93()` populates `struct octep_vf_hw_ops` and calls config init.

## Control Flow
The VF main probe selects this file for CN93/CNF95N/CN98 VF device IDs. Queue setup waits for hardware IDLE bits, programs descriptor base/size registers, configures 64-byte instruction mode and endianness behavior, stores MMIO register pointers in IQ/OQ objects, and sets interrupt thresholds. Open later enables queues and interrupts through the registered ops. Mailbox notifications share queue-0 interrupt delivery: the IOQ handler checks the mailbox interrupt register before scheduling NAPI.

## State And Persistence
Runtime state written by this file includes `oct->conf` queue/MSI-X settings, IQ register pointers, OQ register pointers, mailbox register pointers, hardware ring control, descriptor bases, ring sizes, interrupt thresholds, and enable bits. It does not persist outside hardware registers and the in-memory VF device structure.

## Dependencies And Integration Points
It depends on `octep_vf_regs_cn9k.h` for register definitions, `octep_vf_main.h` for device and ops types, and `octep_vf_config.h` for defaults. It is called by `octep_vf_device_setup()` and used indirectly by `octep_vf_main.c`, `octep_vf_tx.c`, `octep_vf_rx.c`, and `octep_vf_mbox.c` through `hw_ops`.

## Risks And Edge Cases
- Busy-wait loops for IDLE have no explicit timeout; broken hardware can hang setup.
- Queue 0 carries mailbox interrupt side effects; changes to queue interrupt routing must preserve mailbox handling.
- Register reset writes broad masks to doorbell/count registers and must match hardware clear semantics.
- Configuration trusts the rings-per-VF field read from hardware; invalid zero or too-large values would affect allocation and MSI-X setup.

## Test Signals
Probe CN93/CNF95N/CN98 VFs, verify ring count discovery, open/stop queues, send Tx/Rx traffic, receive PF-to-VF link notifications on queue 0, inspect register dumps, test interrupt enable/disable, and run reset/reopen loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cn9k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cnxk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cnxk.c

## Purpose
This file implements CNXK VF hardware operations for OCTEON endpoint VFs, including queue reset/setup, watermark programming, mailbox register binding, queue interrupt handling, enable/disable operations, register reinitialization, and debug register dumping.

## Important APIs, Types, And Functions
- Debug/reset: `cnxk_vf_dump_q_regs()`, `cnxk_vf_reset_iq()`, `cnxk_vf_reset_oq()`, and `octep_vf_reset_io_queues_cnxk()`.
- Config: `octep_vf_init_config_cnxk_vf()` discovers rings-per-VF, sets descriptor counts, buffer size, refill and interrupt thresholds, OQ watermark, and MSI-X count.
- Register setup: `octep_vf_setup_iq_regs_cnxk()` and `octep_vf_setup_oq_regs_cnxk()` program CNXK IQ/OQ CSRs; OQ setup includes `CNXK_VF_SDP_R_OUT_WMARK`.
- Interrupts: `octep_vf_ioq_intr_handler_cnxk()` handles queue interrupts and PF-to-VF mailbox notifications delivered with queue 0.
- Ops registration: `octep_vf_device_setup_cnxk()` fills the VF hardware ops vector.

## Control Flow
VF main setup selects this file for CN10KA/CNF10KA/CNF10KB/CN10KB VF device IDs. IQ setup waits for IDLE, sets 64-byte instruction mode and ESR, writes descriptor base/size, stores doorbell/count/interrupt register pointers, and initializes instruction count. OQ setup waits for IDLE, writes watermark, writes descriptor base/size with retry until the register reflects the DMA address, clears packet/control mode bits, programs buffer size and interrupt moderation, and stores credit/count register pointers. Open/stop use the registered ops to enable/disable queues and interrupts.

## State And Persistence
The file mutates in-memory VF config and per-queue MMIO pointers, plus hardware state for ring base/size, control bits, watermarks, interrupt thresholds/enables, queue enable bits, mailbox interrupt enable, and doorbell/count registers. State is runtime only and reset/recreated across open/stop or device reset.

## Dependencies And Integration Points
It depends on `octep_vf_regs_cnxk.h`, `octep_vf_main.h`, and `octep_vf_config.h`. It integrates through `struct octep_vf_hw_ops` with the generic VF main, Tx, Rx, and mailbox code. Its OQ watermark behavior corresponds to CNXK register definitions and differs from CN9K.

## Risks And Edge Cases
- IQ IDLE wait loops are unbounded; OQ base programming has a bounded retry but can return `-EFAULT` or `-EAGAIN` and abort queue setup.
- Mailbox delivery is coupled to queue 0 interrupt handling.
- Watermark programming is CNXK-specific; incorrect defaults can cause backpressure problems.
- `schedule_timeout_interruptible(1)` loops while enabling IQs rely on process context and can delay open under slow hardware.

## Test Signals
Probe CNXK VFs, verify OQ descriptor base retry success, validate watermark programming, run Tx/Rx traffic with interrupts, test mailbox link notifications, exercise open/stop/reopen, dump queue registers including `ERR_TYPE`, and test failure behavior when OQ setup cannot latch descriptor base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cnxk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_config.h

## Purpose
This header defines VF driver queue, interrupt, MTU, and configuration defaults plus accessor macros and config structures used by chip-specific setup and generic VF queue code.

## Important APIs, Types, And Functions
- Defaults: `OCTEP_VF_IQ_MAX_DESCRIPTORS`, `OCTEP_VF_OQ_MAX_DESCRIPTORS`, `OCTEP_VF_DB_MIN`, `OCTEP_VF_OQ_BUF_SIZE`, `OCTEP_VF_OQ_REFILL_THRESHOLD`, OQ interrupt thresholds, `OCTEP_VF_WAKE_QUEUE_THRESHOLD`, and MTU bounds.
- Accessors: `CFG_GET_IQ_*`, `CFG_GET_OQ_*`, `CFG_GET_PORTS_*`, and `CFG_GET_IOQ_MSIX()`.
- Structures: `struct octep_vf_iq_config`, `struct octep_vf_oq_config`, `struct octep_vf_ring_config`, `struct octep_vf_msix_config`, and `struct octep_vf_config`.

## Control Flow
Chip-specific VF setup initializes an allocated `struct octep_vf_config` with these defaults after reading hardware ring count. Generic queue setup uses the macros to allocate descriptor rings, choose thresholds, program interrupt moderation, and set real queue counts.

## State And Persistence
The header only defines structures. Runtime instances are held in `octep_vf_device->conf`; values are recreated at probe and are not persisted. Some config fields are then reflected into hardware registers during open.

## Dependencies And Integration Points
The header depends on kernel Ethernet and skb buffer-size concepts through source context. It is included by VF main, chip-specific hardware files, mailbox, Tx/Rx queue helpers, and ethtool code.

## Risks And Edge Cases
- Queue descriptor counts are assumed to work with ring masks and should remain powers of two.
- `OCTEP_VF_OQ_BUF_SIZE` uses page-sized skb overhead; architecture page-size differences can change receive buffer behavior.
- `OCTEP_VF_MAX_MTU` is fixed at 10000-byte frame size minus Ethernet header/FCS, while PF may report a different max through mailbox for PF-side MTU.
- `CFG_GET_IQ_INSTR_SIZE()` always returns 64, so 32-byte instruction support is nominal but not active.

## Test Signals
Compile all VF files, verify config initialization for CN9K and CNXK, run queue allocation at discovered ring counts, validate MTU min/max behavior, test OQ refill and interrupt moderation thresholds, and inspect ethtool channel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_ethtool.c

## Purpose
This file implements VF ethtool operations for driver info, link state, statistics strings/counts/values, link mode reporting, and channel counts.

## Important APIs, Types, And Functions
- Stats metadata: `octep_vf_gstrings_global_stats`, `octep_vf_gstrings_tx_q_stats`, and `octep_vf_gstrings_rx_q_stats`.
- Etthool callbacks: `octep_vf_get_drvinfo()`, `octep_vf_get_strings()`, `octep_vf_get_sset_count()`, `octep_vf_get_ethtool_stats()`, `octep_vf_get_link_ksettings()`, and `octep_vf_get_channels()`.
- Link mode mapping: `OCTEP_VF_SET_ETHTOOL_LINK_MODES_BITMAP()` converts OCTEON VF link-mode bits to ethtool link mode bits.
- Registration: `octep_vf_set_ethtool_ops()` assigns `octep_vf_ethtool_ops`.

## Control Flow
VF probe calls `octep_vf_set_ethtool_ops()`. User ethtool stats requests first fetch interface stats from PF via `octep_vf_get_if_stats()`, then combine global hardware stats with per-queue software stats. Link settings requests fetch link info from PF via `octep_vf_get_link_info()`, translate supported/advertised link bitmaps, report autoneg and fibre port mode, and use carrier state to decide whether speed/duplex are known.

## State And Persistence
The file stores no persistent state. It reads and updates `oct->iface_rx_stats`, `oct->iface_tx_stats`, and `oct->link_info` through mailbox calls, then reports in-memory queue stats. Etthool output is a point-in-time snapshot.

## Dependencies And Integration Points
It depends on Linux ethtool APIs, `octep_vf_main.h` for state and exported mailbox-backed helpers, and `octep_vf_config.h` for queue counts. It integrates with PF mailbox bulk reads for stats/link information.

## Risks And Edge Cases
- `octep_vf_get_sset_count()` uses active ring count, but `octep_vf_get_ethtool_stats()` iterates `OCTEP_VF_MAX_QUEUES` for Tx queue stats while strings are emitted only for active queues; this can misalign stats data if active queues are fewer than max.
- Mailbox failures in stats/link fetch are not surfaced strongly to ethtool users; stale cached values may be reported.
- Link mode bitmaps are assigned to `u32` even `link_info` stores `u64`, so upper link mode bits would be truncated if added later.
- The macro body is large and duplicated for supported/advertising; adding new link modes requires careful update.

## Test Signals
Run `ethtool -i`, `ethtool -S`, `ethtool -k`, `ethtool <dev>`, and channel queries on active VFs; compare stats string count to values returned; test link up/down notifications and link-ksettings output; simulate mailbox errors; and validate all supported speeds advertised by firmware are represented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.c

## Purpose
This is the primary PCI and netdev implementation for the OCTEON endpoint Virtual Function driver. It probes supported VF PCI IDs, maps BAR0, selects CN9K/CNXK VF hardware ops, negotiates PF/VF mailbox compatibility, registers the netdev, owns open/stop, transmit, NAPI, MSI-X queue interrupts, mailbox-backed link/Rx/MTU/MAC/offload operations, stats, timeout recovery, and remove cleanup.

## Important APIs, Types, And Functions
- PCI/module surface: `octep_vf_pci_id_tbl`, `octep_vf_driver`, `octep_vf_probe()`, `octep_vf_remove()`, `octep_vf_init_module()`, and `octep_vf_exit_module()`.
- Netdev surface: `octep_vf_netdev_ops` wires `octep_vf_open()`, `octep_vf_stop()`, `octep_vf_start_xmit()`, `octep_vf_get_stats64()`, `octep_vf_tx_timeout()`, `octep_vf_set_mac()`, `octep_vf_change_mtu()`, and `octep_vf_set_features()`.
- Interrupt and NAPI setup: `octep_vf_alloc_ioq_vectors()`, `octep_vf_enable_msix_range()`, `octep_vf_request_irqs()`, `octep_vf_setup_irqs()`, `octep_vf_napi_poll()`, and cleanup counterparts.
- PF mailbox integration: `octep_vf_get_link_status()`, `octep_vf_set_link_status()`, `octep_vf_set_rx_state()`, `octep_vf_get_if_stats()`, `octep_vf_get_link_info()`, and `octep_vf_get_mac_addr()` call mailbox helpers.
- Device setup: `octep_vf_device_setup()` maps BAR0, identifies chip, and calls `octep_vf_device_setup_cn93()` or `octep_vf_device_setup_cnxk()`.

## Control Flow
Probe enables PCI, sets 64-bit DMA mask, requests BARs, allocates a multiqueue Ethernet netdev, initializes `struct octep_vf_device`, maps BAR0 and hardware ops, initializes Tx-timeout work, installs netdev/ethtool ops, sets up the PF/VF mailbox, negotiates mailbox version, fetches firmware info, configures netdev offload features and MTU bounds, retrieves MAC address from PF, and registers the netdev.

Open resets IO queues, allocates IQ/OQ rings, sets up MSI-X and queue IRQs, sets real queue counts, adds/enables NAPI, marks admin up, asks PF to enable Rx, ensures link status is up if needed, enables hardware queues and interrupts, credits OQs, and turns carrier on if PF reports link up. Stop disables carrier and Tx, asks PF to set link/Rx down, disables interrupts and NAPI, frees IRQs and queue resources, disables/resets hardware queues, and returns the device to a closed state.

Transmit is the VF equivalent of the PF path: pad short skb, select queue, build single-buffer or SGL descriptor, add firmware-provided PKIND/front-size and optional checksum/TSO metadata, advance ring indices, maybe stop the subqueue, batch doorbell writes, and free dropped skbs on DMA mapping errors. Tx timeout holds a netdev reference, schedules work, and the work restarts the running netdev under RTNL.

## State And Persistence
State is volatile and stored in `struct octep_vf_device`: config, BAR mapping, firmware info from PF, negotiated mailbox version, queue arrays, stats, link info, mailbox pointer, hardware ops, IRQ vectors, and timeout work. Hardware state includes VF queue registers, MSI-X vectors, mailbox registers, descriptor DMA memory, and PF-maintained VF configuration reached via mailbox.

## Dependencies And Integration Points
The file depends on Linux PCI/netdev/AER/DMA/NAPI/MSI-X APIs, `octep_vf_config.h`, `octep_vf_main.h`, chip-specific VF files, VF Tx/Rx helpers, VF mailbox helpers, and VF ethtool ops. It requires a compatible PF and firmware mailbox protocol for MAC, firmware info, link, stats, MTU, and offload configuration.

## Risks And Edge Cases
- The VF requests only queue MSI-X vectors; mailbox notifications are multiplexed into queue 0 by chip-specific handlers.
- Probe depends on a live PF mailbox. PF absence or protocol mismatch prevents netdev registration.
- The Tx DMA error cleanup path uses SGL length indexes that should be checked against mapping layout.
- `octep_vf_open()` cleanup after `netif_set_real_num_*` failure disables/deletes NAPI even if NAPI was not yet added in that path.
- Feature changes must be accepted by PF; local netdev features are updated only after mailbox success.
- Etthool/stats rely on PF bulk reads and can report stale state if mailbox calls fail.

## Test Signals
Test module load/unload, VF probe with compatible and incompatible PF versions, open/stop/reopen, Tx/Rx traffic, queue-full and timeout recovery, mailbox-backed MAC/MTU/offload changes, link up/down notifications, MSI-X interrupt affinity, DMA debug, PF removal or VF hot-unplug, and netdev registration failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.h

## Purpose
This header defines the VF driver's central device model, PCI IDs, queue limits, hardware operation vector, mailbox structure, link and firmware info, CSR helpers, and exported internal APIs.

## Important APIs, Types, And Functions
- IDs and limits: `OCTEP_PCI_DEVICE_ID_*_VF`, `OCTEP_VF_MAX_QUEUES`, `OCTEP_VF_MAX_IQ`, `OCTEP_VF_MAX_OQ`, and interrupt resend bit constants.
- Ring helpers: `IQ_INSTR_PENDING()` and `IQ_INSTR_SPACE()`.
- Hardware abstraction: `struct octep_vf_hw_ops` defines setup, IRQ, reinit, queue enable/disable, reset, read-index update, and dump hooks.
- Mailbox state: `struct octep_vf_mbox_data`, `struct octep_vf_mbox_wk`, and `struct octep_vf_mbox` hold register pointers, mutex, work item, and bulk read buffer.
- Main state: `struct octep_vf_device` stores config, PCI/netdev pointers, BAR0 mapping, queues, stats, hardware ops, link info, mailbox, negotiated mailbox version, and firmware info.
- CSR helpers: `octep_vf_write_csr*()` and `octep_vf_read_csr*()`.

## Control Flow
VF source files share `struct octep_vf_device` as their context. Probe initializes it, chip-specific setup fills `hw_ops`, queue helpers allocate `iq[]` and `oq[]`, main open/stop calls hardware ops, mailbox helpers update PF-backed state, and ethtool reads stats/link data through exported functions.

## State And Persistence
All defined structures are runtime-only. `mbox_neg_ver` and `fw_info` are negotiated/fetched at probe. Queue arrays, stats, link info, and mailbox buffers are updated while the VF is loaded. BAR0 CSR access depends on `mmio.hw_addr` remaining mapped.

## Dependencies And Integration Points
It includes `octep_vf_tx.h`, `octep_vf_rx.h`, and `octep_vf_mbox.h`, tying the VF device model to queue formats and PF/VF protocol. It exposes prototypes consumed across VF main, chip-specific, Tx/Rx, mailbox, and ethtool files.

## Risks And Edge Cases
- The VF mailbox buffer size is fixed by `OCTEP_PFVF_MBOX_MAX_DATA_BUF_SIZE`; bulk PF responses must fit.
- `hw_ops` must be complete for the selected chip before open; missing function pointers will crash data paths.
- Direct CSR macros assume BAR0 mapping and no external synchronization.
- Link-mode enums mirror PF-side definitions and must stay aligned with firmware/PF payloads.

## Test Signals
Build all VF objects, verify chip setup populates `hw_ops`, confirm mailbox version and firmware info fields after probe, test CSR access through register dumps, validate queue count bounds, and run open/stop/ethtool/mailbox paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.c

## Purpose
This file implements the VF side of the PF/VF mailbox protocol. It sets up mailbox registers, negotiates protocol version, sends synchronous commands to PF, performs fragmented bulk reads for link info and stats, applies mailbox-backed netdev operations, processes PF link notifications, and notifies PF on VF removal.

## Important APIs, Types, And Functions
- Lifecycle: `octep_vf_setup_mbox()` allocates mailbox state, binds chip-specific registers, initializes work, and sets initial negotiated version; `octep_vf_delete_mbox()` cancels work and frees it.
- Version and async work: `octep_vf_mbox_version_check()` negotiates with PF; `octep_vf_mbox_work()` processes PF-to-VF notifications, currently link-status changes.
- Command core: `__octep_vf_mbox_send_cmd()` writes a command word and polls for PF response; `octep_vf_mbox_send_cmd()` serializes commands and checks version support.
- Bulk reads: `octep_vf_mbox_bulk_read()` sends an initial request to get payload length and then reads six-byte fragments into `mbox_data.recv_data`.
- Netdev helpers: `octep_vf_mbox_set_mtu()`, `octep_vf_mbox_set_mac_addr()`, `octep_vf_mbox_get_mac_addr()`, `octep_vf_mbox_set_rx_state()`, `octep_vf_mbox_set_link_status()`, `octep_vf_mbox_get_link_status()`, `octep_vf_mbox_dev_remove()`, `octep_vf_mbox_get_fw_info()`, and `octep_vf_mbox_set_offloads()`.

## Control Flow
Probe sets up the mailbox before registering the netdev. Commands are serialized with `mbox->lock`; the VF writes a command word to `mbox_write_reg`, then polls the same register until PF overwrites it with a different word. ACK/NACK type bits determine success. Bulk reads first get total length from PF, then repeatedly set `frag=1` and copy up to six bytes from each response into the local receive buffer.

PF notifications are delivered by chip-specific interrupt handlers scheduling `octep_vf_mbox_work()`. The worker reads `mbox_read_reg`, decodes the notification opcode, and updates `link_info.oper_up` plus carrier state for link-status notifications.

## State And Persistence
Runtime state includes `oct->mbox`, mailbox register pointers, `mbox_neg_ver`, `mbox_data.data_index`, `mbox_data.recv_data`, and `oct->fw_info` fetched from PF. PF-side persistent-ish runtime state is changed by commands for MAC, MTU, Rx/link status, offloads, and VF removal, but no disk state is written.

## Dependencies And Integration Points
This file depends on `octep_vf_main.h`, `octep_vf_config.h`, Linux PCI/netdevice/workqueue APIs, and a PF implementing the mirrored protocol. It is called by VF probe, open/stop, netdev MAC/MTU/features operations, ethtool stats/link functions, and remove.

## Risks And Edge Cases
- The command timeout is `8000` polls with 1-1.5 ms sleeps, so a wedged PF can stall operations for seconds.
- Bulk receive buffer is 320 bytes, while PF-side maximum is 384 bytes; large stat/link payload growth can overflow or truncate unless both sides are updated.
- `octep_vf_mbox_set_mtu()` validates frame size against `ETH_MAX_MTU`, which may be lower than the driver's advertised VF max frame intent.
- `octep_vf_mbox_set_offloads()` checks `rsp.s_link_state.type` rather than `rsp.s_offloads.type`; the bitfield location is equivalent for type, but the member choice is misleading.
- Commands without a response, such as device remove, return immediately after writing; PF acknowledgement is not verified.

## Test Signals
Test PF/VF version negotiation, every mailbox command ACK/NACK path, timeout behavior with PF unavailable, link notification carrier changes, bulk stats and link-info reads, MAC and MTU changes from VF, offload feature changes, VF remove notification, and concurrent ethtool/netdev requests for mutex serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.h

## Purpose
This header defines the VF-side PF/VF mailbox protocol ABI, including versions, opcodes, word types, status codes, link enums, timing and buffer limits, the packed mailbox word union, and exported VF mailbox helper APIs.

## Important APIs, Types, And Functions
- Protocol versioning: `enum octep_pfvf_mbox_version` and `OCTEP_PFVF_MBOX_VERSION_CURRENT`.
- Opcodes: version, MTU, MAC, link info, stats, Rx state, link status, device remove, firmware info, offloads, and link notification.
- Status and timing: `OCTEP_PFVF_MBOX_TIMEOUT_WAIT_COUNT`, `OCTEP_PFVF_MBOX_TIMEOUT_WAIT_UDELAY`, retries, max inline data size, and max bulk data buffer.
- Payload ABI: `union octep_pfvf_mbox_word` overlays a 64-bit word with typed views for command data, fragments, version, MAC, MTU, link state/status, firmware info, and offloads.
- Exported helpers: setup/delete, send command, bulk read, version check, set/get MAC, set MTU, set Rx/link state, get link status, device remove, firmware info, and offload setting.

## Control Flow
The union's opcode/type fields let VF code construct a command word and PF code return an ACK/NACK in the same register. Bulk commands use the `s_data` view and the fragment bit. The function prototypes are used by VF main and ethtool code to make PF-backed operations look like local driver operations.

## State And Persistence
The header defines no live storage. It constrains mailbox users through fixed protocol values and payload sizes. Negotiated version and bulk buffers are stored in `struct octep_vf_device` and `struct octep_vf_mbox` from `octep_vf_main.h`.

## Dependencies And Integration Points
The definitions must match PF-side `octep_pfvf_mbox.h`. It is included by `octep_vf_main.h` and implemented by `octep_vf_mbox.c`. The protocol is coupled to PF firmware control operations because PF services most VF commands by proxying to firmware.

## Risks And Edge Cases
- PF and VF headers duplicate enums and union layout; any mismatch breaks ABI.
- `OCTEP_PFVF_MBOX_MAX_DATA_BUF_SIZE` is smaller than the PF header's staged data size, which is a compatibility risk for bulk stats.
- Bitfield ABI and `__packed` layout must remain compiler-compatible across PF/VF builds.
- The timeout delay macro is not directly used by the implementation, which hard-codes `usleep_range(1000, 1500)`.

## Test Signals
Compile PF and VF together, compare opcode/version constants, run mailbox version negotiation, exercise each exported helper with PF ACK and NACK, validate fragmented reads near buffer limits, and test notification decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.h -->
