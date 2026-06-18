# subset-b-004499 research

Grouped research for ixgbe mailbox, PHY/module access, PTP, SR-IOV, sysfs thermal, Flow Director model helpers, and Tx/Rx common declarations.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.c

## Purpose
`ixgbe_mbx.c` implements the physical-function side of the ixgbe PF/VF mailbox transport. It provides generic wrapper entry points through `hw->mbx.ops`, PF mailbox register operations, posted read/write helpers with polling, mailbox event checks, statistics updates, and PF mailbox initialization for SR-IOV capable MACs.

## Important APIs and functions
The public wrapper APIs are `ixgbe_read_mbx`, `ixgbe_write_mbx`, `ixgbe_check_for_msg`, `ixgbe_check_for_ack`, and `ixgbe_check_for_rst`. They validate `hw->mbx.ops`, enforce mailbox size rules, and delegate to the operation table. `ixgbe_read_mbx` clamps reads to `mbx->size`, while `ixgbe_write_mbx` rejects oversized writes with `-EINVAL`.

The posted helpers `ixgbe_read_posted_mbx` and `ixgbe_write_posted_mbx` add polling around the raw operations. `ixgbe_poll_for_msg` and `ixgbe_poll_for_ack` loop until the operation-specific check returns success or `mbx->timeout` expires, sleeping `mbx->usec_delay` between attempts.

The PF implementation is in `ixgbe_check_for_msg_pf`, `ixgbe_check_for_ack_pf`, `ixgbe_check_for_rst_pf`, `ixgbe_obtain_mbx_lock_pf`, `ixgbe_write_mbx_pf`, and `ixgbe_read_mbx_pf`. The exported operation table `mbx_ops_generic` binds these methods. `ixgbe_init_mbx_params_pf`, under `CONFIG_PCI_IOV`, initializes size, timeout/delay, and stats for supported PF MAC generations.

## Control flow
Caller code in SR-IOV paths uses the wrapper APIs. The wrapper locates `struct ixgbe_mbx_info` in `hw->mbx`, validates operation availability, then dispatches to PF-specific handlers. PF message and ACK detection reads `IXGBE_MBVFICR(index)`, tests the VF bit, writes the bit back to clear it, and increments request or ACK counters. Reset detection reads `IXGBE_VFLRE` on 82599 or `IXGBE_VFLREC` on newer MACs, clears reset-complete bits, and increments reset counters.

For PF writes, `ixgbe_write_mbx_pf` first claims ownership with `IXGBE_PFMAILBOX_PFU`, flushes stale message and ACK state, writes each u32 to `IXGBE_PFMBMEM(vf_number)`, then writes `IXGBE_PFMAILBOX_STS` to interrupt the VF and release the buffer. PF reads mirror that flow: claim lock, copy words from `IXGBE_PFMBMEM`, then acknowledge and release with `IXGBE_PFMAILBOX_ACK`.

## State and persistence
Runtime state lives in `hw->mbx`: configured size, timeout/delay, operation table, and counters for transmitted messages, received messages, requests, ACKs, and resets. Mailbox payload and ownership are held in device registers, not persistent storage. Register writes both signal events and clear event bits, so read/check operations have side effects.

## Dependencies and integration points
The file depends on `ixgbe.h`, `ixgbe_mbx.h`, PCI/SR-IOV build support, MMIO helpers such as `IXGBE_READ_REG`, `IXGBE_WRITE_REG`, and `IXGBE_WRITE_REG_ARRAY`, and MAC type values from the ixgbe type system. It is consumed mainly by `ixgbe_sriov.c`, which dispatches VF mailbox requests and sends PF replies.

## Risks and edge cases
Mailbox operations are register side-effect heavy. A missed clear, failed PF ownership claim, or wrong VF index can lose a message or wedge VF/PF negotiation. Posted mailbox helpers return `-EIO` when no timeout is configured, so PF-side users must not assume posted operation support unless timeout/delay are initialized. Reset handling writes `IXGBE_VFLREC` even after reading `IXGBE_VFLRE` for 82599, which is intentional register behavior but should be regression-tested on older hardware.

## Test signals
Useful signals include SR-IOV VF reset and mailbox negotiation success, incrementing mailbox stats under VF traffic, successful ACK/NACK delivery for each mailbox command, and absence of mailbox timeouts during VF driver load/unload. Fault tests should cover oversized writes, unavailable `mbx->ops`, VFs that never ACK, VF reset events, and multiple VFs mapped across both `MBVFICR` index groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.h

## Purpose
`ixgbe_mbx.h` defines the PF/VF mailbox ABI for ixgbe. It contains mailbox sizes, mailbox register offsets and bit definitions, VF request opcodes, ACK/NACK/CTS flags, PF/VF API revision identifiers, negotiated feature bits, wrapper prototypes, and the mailbox operation table.

## Important APIs, types, and constants
`IXGBE_VFMAILBOX_SIZE` defines the 16-word, 64-byte mailbox payload. `IXGBE_PFMAILBOX_*` flags represent PF/VF ownership, status, ACK, and VF reset control. `IXGBE_MBVFICR_*` masks describe interrupt-cause bits for VF requests and ACKs.

`enum ixgbe_pfvf_api_rev` is the versioned PF/VF mailbox API contract. Existing numeric values must remain stable; new revisions are appended before `ixgbe_mbox_api_unknown`. The command namespace includes reset, MAC, multicast, VLAN, MTU/LPE, MACVLAN, API negotiation, queue discovery, RETA/RSS key reads, xcast mode updates, IPsec SA operations, link-state queries, PF link-state queries, and feature negotiation.

`struct ixgbe_mbx_operations` is the dispatch table used by `hw->mbx.ops`, with raw read/write methods, posted read/write methods, and event checks for message, ACK, and reset. The file declares `mbx_ops_generic` as the shared PF implementation.

## Control flow and integration
The header is the shared contract between mailbox transport code and SR-IOV policy code. `ixgbe_mbx.c` implements the transport and exports wrappers. `ixgbe_sriov.c` interprets `IXGBE_VF_*` opcodes, applies PF policy, and replies with the high-bit message type flags declared here.

## State and persistence
The header defines protocol constants only. Persistent ABI compatibility matters because VF drivers can be older or newer than the PF driver. The API revision enum and opcode values must not be reordered or repurposed.

## Dependencies
It includes Linux integer types and forward-declares `struct ixgbe_hw`. Register macros such as `IXGBE_PFMAILBOX(vf)` and payload offsets are consumed by the transport implementation and by VF command handlers.

## Risks and edge cases
Changing opcode values, API revision ordering, or mailbox word layout can break guest VF drivers. `IXGBE_SUPPORTED_FEATURES` currently advertises IPsec support only; adding feature bits must be matched with command dispatch support and VF compatibility checks. Message flag bits occupy the high nibble, while `IXGBE_VT_MSGINFO_MASK` uses bits 23:16, so new commands must avoid overlapping those fields.

## Test signals
Compatibility tests should load VF drivers using multiple API revisions and verify negotiation, reset, queue discovery, RSS query gating, IPsec feature negotiation, and ACK/NACK semantics. ABI review should confirm all new mailbox commands fit within the 16-word payload and keep existing enum values stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_model.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_model.h

## Purpose
`ixgbe_model.h` defines a compact packet parser and field-programming model used for ixgbe Flow Director classification. It maps packet header offsets and next-header jumps into `struct ixgbe_fdir_filter` and `union ixgbe_atr_input` fields.

## Important APIs, types, and tables
`struct ixgbe_mat_field` describes a matchable field: byte offset, programming callback, and ATR flow type. `struct ixgbe_jump_table` carries the current match table, filter input, mask, link handle, and child-location bitmap. `struct ixgbe_nexthdr` describes parser transitions using a header offset, shift/mask for next-header location, match criteria, and target field table.

Inline helpers `ixgbe_mat_prgm_sip`, `ixgbe_mat_prgm_dip`, and `ixgbe_mat_prgm_ports` program IPv4 source/destination addresses and TCP/UDP port pairs into Flow Director input and mask structures. Static tables `ixgbe_ipv4_fields`, `ixgbe_tcp_fields`, `ixgbe_udp_fields`, and `ixgbe_ipv4_jumps` describe IPv4, TCP, and UDP parsing.

## Control flow
The model is data-driven. A caller walks fields in a protocol table until a terminal `{ .val = NULL }`, calling each `val` function to store extracted values and masks. For IPv4, the jump table checks protocol bytes at offset 8 and jumps to TCP or UDP field tables. `IXGBE_MAX_HW_ENTRIES` caps hardware entries exposed by this model.

## State and persistence
The header stores no runtime state beyond static parser tables. Runtime state is passed through `ixgbe_jump_table`, `ixgbe_fdir_filter`, and `ixgbe_atr_input`. The byte-order casts use `__force` to store raw values into big-endian fields expected by Flow Director hardware programming.

## Dependencies and integration points
It includes `ixgbe.h` and `ixgbe_type.h` for Flow Director structures, ATR flow type constants, and endian annotations. Integration is with ixgbe classifier/offload code that translates higher-level flow rules into hardware Flow Director entries.

## Risks and edge cases
The model is narrow: it covers IPv4 source/destination and TCP/UDP ports, not IPv6 or deeper encapsulation. Header offsets are fixed and assume the caller already normalized packet layout enough for these offsets to be valid. Incorrect mask byte order or port packing would silently install wrong Flow Director filters.

## Test signals
Tests should validate generated Flow Director entries for IPv4 TCP and UDP source/destination address and port rules, including masks. Negative tests should cover unsupported protocol jumps, terminal table handling, maximum entry limits, and byte-order correctness against known packet/filter tuples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_model.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.c

## Purpose
`ixgbe_phy.c` implements generic ixgbe PHY, MDIO, MII bus, SFP/QSFP module, I2C EEPROM, link advertisement, PHY reset, overtemperature, and copper PHY power support. It is the hardware-facing layer that identifies PHY types, reads and writes MDIO/I2C registers with the required synchronization, programs link capabilities, validates optical modules, and exposes an MDIO bus to the kernel.

## Important APIs and functions
PHY identity and reset are handled by `ixgbe_identify_phy_generic`, `ixgbe_probe_phy`, `ixgbe_get_phy_id`, `ixgbe_get_phy_type_from_id`, `ixgbe_reset_phy_generic`, and `ixgbe_reset_phy_nl`. MDIO register access is split into unlocked MDI transactions (`ixgbe_read_phy_reg_mdi`, `ixgbe_write_phy_reg_mdi`) and locked wrappers (`ixgbe_read_phy_reg_generic`, `ixgbe_write_phy_reg_generic`) that acquire `hw->phy.phy_semaphore_mask`.

MII bus integration is provided by `ixgbe_mii_bus_init` and its Clause 22/45 read/write helpers. X550EM_A gets special handlers that include `IXGBE_GSSR_TOKEN_SM` and `IXGBE_GSSR_PHY0_SM`, and `ixgbe_x550em_a_has_mii` ensures only the first SoC function registers the shared MDIO bus.

Link setup and capability logic is in `ixgbe_setup_phy_link_generic`, `ixgbe_setup_phy_link_speed_generic`, `ixgbe_get_copper_link_capabilities_generic`, `ixgbe_get_copper_speeds_supported`, `ixgbe_check_phy_link_tnx`, and `ixgbe_setup_phy_link_tnx`. Module handling is in `ixgbe_identify_module_generic`, `ixgbe_identify_sfp_module_generic`, `ixgbe_identify_qsfp_module_generic`, and `ixgbe_get_sfp_init_sequence_offsets`.

I2C support includes combined 16-bit operations (`ixgbe_read_i2c_combined_generic_int`, `ixgbe_write_i2c_combined_generic_int`), EEPROM helpers (`ixgbe_read_i2c_eeprom_generic`, `ixgbe_read_i2c_sff8472_generic`, `ixgbe_write_i2c_eeprom_generic`), byte operations with locked and unlocked variants, and bit-banged primitives for start, stop, clock/data transitions, ACK polling, and bus clear.

## Control flow
PHY identification first sets a default semaphore mask based on LAN ID, then either probes a management-selected PHY address or scans all possible addresses. A successful probe uses `mdio45_probe`, reads PHY IDs, maps known IDs to ixgbe PHY types, and falls back to copper or generic PHY based on extended PMA abilities.

Generic reset identifies the PHY if needed, skips reset for no PHY, overtemperature shutdown, or management firmware veto, writes `MDIO_CTRL1_RESET`, then polls for self-clear or X550EM external-t PHY alarm completion. NL PHY reset performs a reset, retrieves EEPROM offsets for the SFP init sequence, then interprets EEPROM control/data/delay records to program PHY PMA/PMD registers.

Link setup reads supported speeds, filters advertised speeds through `hw->phy.autoneg_advertised`, writes 10G/5G/2.5G/1G/100M advertisement registers, and restarts autoneg unless management veto is active. TNX setup follows a similar path with TNX-specific registers.

SFP/QSFP identification reads EEPROM identifiers and capability bytes, derives `hw->phy.sfp_type`, sets `sfp_setup_needed` when the module changes, detects multispeed fiber, assigns a vendor-specific `hw->phy.type`, and enforces Intel optics policy unless device capabilities or `allow_unsupported_sfp` permit otherwise. I2C read/write paths acquire the SW/FW semaphore when requested, bit-bang device address, register offset, data and ACKs, retry on failure, and clear the bus before retrying.

## State and persistence
The file updates `hw->phy.phy_semaphore_mask`, `hw->phy.mdio.prtad`, `hw->phy.id`, `hw->phy.revision`, `hw->phy.type`, `hw->phy.sfp_type`, `hw->phy.sfp_setup_needed`, `hw->phy.multispeed_fiber`, `hw->phy.speeds_supported`, and `hw->phy.autoneg_advertised`. It also stores the registered `mii_bus` in `adapter->mii_bus`. Hardware state persists in MDIO, MSCA/MSRWD, I2CCTL, PHY control, AN advertisement, EEPROM, and module EEPROM registers until hardware reset or later driver writes.

## Dependencies and integration points
This file depends on Linux PCI, delay, iopoll, scheduler, MDIO/MII bus APIs, ixgbe MMIO helpers, `hw->mac.ops` for SW/FW semaphore and media/capability callbacks, `hw->eeprom.ops.read`, and netdev/device-managed allocation via the adapter backpointer. It integrates with probe/open/reset paths, ethtool link settings, module detection, thermal/sysfs support through PHY/module data, and board-specific MAC operation tables.

## Risks and edge cases
The main risks are hardware timeouts, semaphore contention, management firmware vetoes, unsupported or misidentified optics, and bus lockups. I2C operations have side effects on shared module buses and rely on exact timing and ACK behavior. `ixgbe_reset_phy_nl` interprets EEPROM data blocks and can fail on corrupt offsets or bad control words. X550EM_A MDIO bus ownership is topology-specific and assumes fixed root ports. Unsupported SFP enforcement can intentionally reject working third-party optics unless override is enabled.

## Test signals
Tests and lab validation should include PHY discovery across known IDs, absence of PHY on fiber media, MDIO Clause 22/45 reads through the registered bus, SW/FW semaphore contention, SFP/QSFP insert/remove and vendor policy handling, corrupted or missing EEPROM offset handling, I2C NACK and stuck-bus recovery, autoneg advertisement for 100M/1G/2.5G/5G/10G, management-veto reset suppression, overtemperature behavior, and copper PHY low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.h

## Purpose
`ixgbe_phy.h` is the PHY/module access contract for ixgbe. It declares EEPROM offsets, SFP/QSFP capability masks, vendor OUIs, I2C timing constants, CS4227/port-expander constants, flow-control bits, overtemperature registers, and prototypes for PHY, MDIO, module, and I2C helpers.

## Important APIs and constants
The header exposes `ixgbe_mii_bus_init`, PHY identity/reset/read/write helpers, link setup and capability helpers, TNX-specific link methods, NL reset, copper power control, module identification, SFP init-sequence lookup, overtemperature check, byte-level I2C EEPROM/SFF8472 access, and combined I2C operations.

SFP/QSFP offsets and masks identify module type, 1G/10G capabilities, direct-attach cable type, bitrate, cable length, SFF-8472 support, soft rate select, diagnostic monitoring, and vendor OUI bytes. I2C timing constants encode standard-mode SDA/SCL setup, hold, high, low, rise, fall, stop, and bus-free timings used by the bit-banged implementation.

## Control flow and integration
Implementation code uses the offsets and masks to read module EEPROM, classify module types, enforce supported optics policy, and determine PHY initialization sequences. Link setup and reset code use prototypes here through MAC operation tables and `hw->phy.ops`. The header is included by `ixgbe_phy.c` and by board-specific ixgbe code that configures PHY ops.

## State and persistence
The header itself has no mutable state. It defines constants that map persistent EEPROM content and volatile PHY/I2C/MDIO hardware registers. Because these values describe external module EEPROM layouts and hardware register programming, compatibility depends on keeping the constants aligned with hardware specifications.

## Dependencies
It includes `ixgbe_type.h` for core hardware types, link speed types, and enum definitions. The function declarations depend on `struct ixgbe_hw`, `ixgbe_link_speed`, and Linux integer types available through included ixgbe headers.

## Risks and edge cases
Wrong offsets or masks can misclassify optics, advertise invalid link capabilities, or read/write the wrong I2C device. Timing constants are used in low-level bus toggling, so casual changes can break marginal modules. CS4227 and port-expander constants are hardware-specific and should not be generalized without board validation.

## Test signals
Validation should compare SFP/QSFP EEPROM parsing against known modules, confirm I2C timing-sensitive modules still read reliably, verify exported prototypes match operation table assignments, and exercise copper/fiber/QSFP boards with PHY reset, autonegotiation, and low-power operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ptp.c

## Purpose
`ixgbe_ptp.c` implements Precision Time Protocol hardware clock support for ixgbe devices. It maps hardware SYSTIME registers into Linux `cyclecounter`/`timecounter`, registers a PHC with the PTP subsystem, supports frequency and time adjustment, configures hardware timestamp filters, handles TX/RX hardware timestamps, recovers timestamp hangs, and optionally drives PPS/clock output on SDP0.

## Important APIs and functions
PHC operations are installed by `ixgbe_ptp_create_clock` and include `ixgbe_ptp_adjfine_82599`, `ixgbe_ptp_adjfine_X550`, `ixgbe_ptp_adjtime`, `ixgbe_ptp_gettimex`, `ixgbe_ptp_settime`, and `ixgbe_ptp_feature_enable`. Lifecycle entry points are `ixgbe_ptp_init`, `ixgbe_ptp_reset`, `ixgbe_ptp_suspend`, and `ixgbe_ptp_stop`.

Cyclecounter support is split by hardware generation. `ixgbe_ptp_read_82599` reads raw 64-bit fixed-point SYSTIME. `ixgbe_ptp_read_X550` converts X550-style high/low registers into a nanosecond-like cycle value. `ixgbe_ptp_start_cyclecounter` selects read functions, masks, multipliers, shifts, and TIMINCA programming based on MAC type and link speed.

Timestamping APIs include `ixgbe_ptp_hwtstamp_get`, `ixgbe_ptp_hwtstamp_set`, `ixgbe_ptp_set_timestamp_mode`, `ixgbe_ptp_tx_hwtstamp_work`, `ixgbe_ptp_rx_pktstamp`, `ixgbe_ptp_rx_rgtstamp`, `ixgbe_ptp_tx_hang`, and `ixgbe_ptp_rx_hang`. PPS support uses `ixgbe_ptp_setup_sdp_X540`, `ixgbe_ptp_setup_sdp_X550`, and `ixgbe_ptp_check_pps_event`.

## Control flow
Initialization creates or reuses a PHC, initializes `tmreg_lock`, sets up TX timestamp work, resets timestamp hardware, initializes SYSTIME to real time through the timecounter, and marks PTP running. Reset re-applies timestamp filter settings, reprograms TIMINCA/cyclecounter, clears SYSTIME registers, initializes the timecounter from `ktime_get_real`, and re-enables SDP output if configured.

Frequency adjustment computes a new TIMINCA value from `adapter->base_incval` on 82599/X540 or from the X550/E610 base period on newer MACs. Time adjustment and settime only update the software timecounter under `tmreg_lock`; the hardware SYSTIME register remains a cycle source.

Hardware timestamp configuration validates requested TX and RX modes, maps supported filters to `TSYNCTXCTL`, `TSYNCRXCTL`, `RXMTRL`, and `ETQF`, normalizes some requested RX filters to broader hardware-supported modes, clears stale TX/RX timestamp registers, and stores the accepted config in `adapter->tstamp_config`.

TX timestamping allows one outstanding skb tracked by `adapter->ptp_tx_skb` and `__IXGBE_PTP_TX_IN_PROGRESS`. Work polls `TSYNCTXCTL_VALID`, reads TX timestamp registers, converts through the timecounter, notifies the stack with `skb_tstamp_tx`, frees the skb, and clears state. RX timestamping either reads an appended packet timestamp or latched RXSTMP registers and converts it into skb hwtstamps.

## State and persistence
Key state lives in `adapter->hw_cc`, `adapter->hw_tc`, `adapter->base_incval`, `adapter->tmreg_lock`, `adapter->ptp_caps`, `adapter->ptp_clock`, `adapter->ptp_setup_sdp`, `adapter->tstamp_config`, `adapter->ptp_tx_skb`, `adapter->ptp_tx_start`, `adapter->last_overflow_check`, `adapter->last_rx_ptp_check`, and PTP-related adapter state/flag bits. Hardware state is in SYSTIME, TIMINCA, TSYNC, TSAUXC, ESDP/TSSDP, target time, and timestamp registers. PHC registration is kernel runtime state and is removed by `ixgbe_ptp_stop`.

## Dependencies and integration points
The file depends on Linux PTP, clocksource/timecounter, skb timestamp APIs, workqueues, spinlocks, netdev hwtstamp ioctl plumbing, and ixgbe interrupt/watchdog paths. It integrates with transmit code for requesting timestamps, receive code for consuming timestamps, link-change paths via `ixgbe_ptp_start_cyclecounter`, reset paths via `ixgbe_ptp_reset`, and interrupt handling for PPS events.

## Risks and edge cases
PTP behavior is hardware-generation-specific. 82599/X540 SYSTIME overflow requires periodic reads, while X550/E610 represent time differently and may need multiplier correction for non-300MHz revisions. Incorrect lock use around `timecounter` can corrupt PHC time. Timestamp filters are broader than some user requests, so user-visible config normalization is important. TX timestamp hangs can retain skb references unless watchdog cleanup runs. RX timestamp registers can latch indefinitely if hardware drops a timestamped packet.

## Test signals
Tests should validate PHC registration by MAC type, `phc2sys`/`ptp4l` operation, adjfine and settime monotonic behavior, link-speed TIMINCA recalculation on 82599/X540, hwtstamp get/set normalization for supported and unsupported filters, one-at-a-time TX timestamp locking, TX timeout cleanup counters, RX register hang recovery, appended RX timestamp handling, PPS enable/disable, suspend/resume retention of timestamp settings, and no PTP registration on unsupported devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.c

## Purpose
`ixgbe_sriov.c` implements SR-IOV PF-side management for ixgbe. It enables and disables VFs, allocates per-VF policy state, handles PCI SR-IOV configuration, dispatches VF mailbox commands, programs VF MAC/VLAN/multicast/RSS/link/rate/spoofing state, reacts to VF resets and malicious driver detection, and exposes netdev `ndo_set_vf_*` controls.

## Important APIs and functions
SR-IOV lifecycle functions include `ixgbe_enable_sriov`, `__ixgbe_enable_sriov`, `ixgbe_disable_sriov`, `ixgbe_pci_sriov_configure`, `ixgbe_pci_sriov_enable`, and `ixgbe_pci_sriov_disable`. VF device references are tracked by `ixgbe_get_vfs`, and extra VF MACVLAN filter storage is allocated by `ixgbe_alloc_vf_macvlans`.

Mailbox handling centers on `ixgbe_msg_task`, `ixgbe_rcv_msg_from_vf`, `ixgbe_vf_reset_msg`, `ixgbe_rcv_ack_from_vf`, `ixgbe_ping_vf`, and `ixgbe_ping_all_vfs`. Command handlers cover VF MAC, multicast, VLAN, LPE/MTU, MACVLAN, API negotiation, queue discovery, RETA/RSS key reads, xcast mode, link state, PF link state, feature negotiation, and IPsec SA add/delete.

Administrative netdev APIs include `ixgbe_ndo_set_vf_mac`, `ixgbe_ndo_set_vf_vlan`, `ixgbe_ndo_set_vf_bw`, `ixgbe_ndo_set_vf_spoofchk`, `ixgbe_ndo_set_vf_rss_query_en`, `ixgbe_ndo_set_vf_trust`, `ixgbe_ndo_get_vf_config`, and `ixgbe_ndo_set_vf_link_state`. Helper functions program hardware state in VFTA/VLVF/VLVFB, VMVIR, VMOLR, VFTE/VFRE, QDE, MAC filters, MTA multicast tables, and rate-control registers.

## Control flow
Enabling SR-IOV rejects XDP coexistence, sets SR-IOV/VMDq flags, allocates `adapter->vfinfo`, initializes default VF policy, sets VMDq offsets, enables VEB switching, limits traffic classes based on VF count, disables RSC, optionally creates PCI VFs, resets/reinitializes the adapter, and takes references to VF PCI devices. Disabling first sets `num_vfs` to zero under `vfs_lock`, releases VF PCI references, frees `vfinfo` and MACVLAN storage, disables MDD and PCI SR-IOV where safe, updates VMDq/RSS limits, and waits for cleanup.

The mailbox task first checks MDD, then under `vfs_lock` scans each VF for reset, message, and ACK events. Reset events clear VLANs and multicast state, restore PF-assigned VLANs, reset offloads and anti-spoofing, clear IPsec state and MACVLAN filters, reset API revision, restart VF queues, clear the mailbox, program VF MAC, enable drop behavior, set clear-to-send, and reply with ACK/NACK plus the permanent MAC payload. Non-reset messages are rejected until `clear_to_send` is true. After dispatch, the PF replies with ACK or NACK plus CTS.

Administrative `ndo_set_vf_*` calls validate VF index and arguments, update `adapter->vfinfo`, program hardware filters/registers, and often require VF reload or ping/reset to apply. Trust and link-state changes clear `clear_to_send` and ping the VF so the guest rebuilds state.

## State and persistence
Core runtime state is in `adapter->num_vfs`, `adapter->vfinfo[]`, `adapter->vf_mvs`, `adapter->mv_list`, `adapter->flags`, `adapter->flags2`, `adapter->ring_feature`, `adapter->bridge_mode`, `adapter->dcb_cfg`, `adapter->vf_rate_link_speed`, `adapter->fwd_bitmask`, and `adapter->vfs_lock`. Per-VF state includes MAC address, PF-set MAC flag, PF VLAN/QoS, spoof checking, trust, RSS-query permission, link state/link enable, xcast mode, TX rate, multicast hashes, VF API revision, clear-to-send, and PCI VF device pointer. Hardware state persists in filter tables and VF enable/drop/rate/spoofing registers until reset or explicit cleanup.

## Dependencies and integration points
The file depends on PCI SR-IOV APIs, Linux netdev VF configuration APIs, mailbox transport from `ixgbe_mbx.c`, ixgbe MAC ops for anti-spoofing/MDD/VFTA, core filter helpers such as `ixgbe_add_mac_filter`, `ixgbe_del_mac_filter`, `ixgbe_set_rx_mode`, `ixgbe_full_sync_mac_table`, VLAN promisc helpers, IPsec VF helpers, DCB/traffic-class state, XDP state, and reset/reinit paths such as `ixgbe_sriov_reinit`.

## Risks and edge cases
SR-IOV state spans PCI, PF software, VF software, and hardware tables. Risks include races with VF teardown, freeing `vfinfo` while events are pending, inability to disable assigned VFs, mailbox commands before reset completion, RAR/MTA/VLVF exhaustion, stale PF-assigned VLAN restrictions, anti-spoofing interactions with MACVLAN filters, link-speed changes invalidating rate limits, and MDD recovery requiring guest VF queue rebuild. XDP and SR-IOV are explicitly incompatible here.

## Test signals
Validation should cover enabling/disabling VFs via module parameter and PCI sysfs, pre-existing VF adoption, assigned VF disable failure, VF reset handshake, every mailbox opcode with ACK/NACK paths, admin MAC/VLAN/link/trust/spoof/RSS/rate changes, VF reload requirements, multicast restore after PF multicast changes, VLAN table cleanup, max VF limits under 1/4/8 traffic classes and offloaded macvlans, MDD detection/restoration, XDP rejection, and rate-limit disable after link-speed changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.h

## Purpose
`ixgbe_sriov.h` declares the PF-side SR-IOV management interface used by the ixgbe core driver and defines VF-count limits for different traffic-class configurations. It also provides a small inline helper for programming VF default VLAN insertion.

## Important APIs and constants
`IXGBE_MAX_VFS_DRV_LIMIT` caps driver-created VFs at one less than the hardware VF function count so the PF retains resources. `IXGBE_MAX_VFS_1TC`, `IXGBE_MAX_VFS_4TC`, and `IXGBE_MAX_VFS_8TC` express VF limits based on traffic-class count.

The header declares SR-IOV lifecycle (`ixgbe_enable_sriov`, `ixgbe_disable_sriov`, `ixgbe_pci_sriov_configure`), mailbox/event work (`ixgbe_msg_task`, `ixgbe_ping_all_vfs`, `ixgbe_set_all_vfs`, `ixgbe_check_mdd_event`), VF PCI callbacks (`ixgbe_vf_configuration`), multicast restore, link/rate helpers, and netdev VF controls for MAC, VLAN, bandwidth, spoof checking, RSS query, trust, config retrieval, and link state.

`ixgbe_set_vmvir` writes `IXGBE_VMVIR(vf)` with VLAN ID, QoS priority, and `IXGBE_VMVIR_VLANA_DEFAULT` to configure VF transmit VLAN insertion.

## Control flow and integration
Core ixgbe probe, remove, reset, watchdog, netdev ops, and PCI SR-IOV callbacks include this header to invoke the implementation in `ixgbe_sriov.c`. The inline VMVIR helper is used by reset and VLAN configuration paths to keep VLAN insertion programming consistent.

## State and persistence
The header has no state. Its APIs manipulate adapter-level VF state and hardware registers through `struct ixgbe_adapter` and `struct ixgbe_hw`. The inline helper directly persists VLAN insertion configuration in the VMVIR hardware register until reset or a later write.

## Dependencies
It relies on ixgbe core type declarations being available before inclusion, including `struct ixgbe_adapter`, `struct pci_dev`, `struct net_device`, and VLAN constants. Some declarations are gated by `CONFIG_PCI_IOV`.

## Risks and edge cases
VF limit constants are policy-sensitive because they protect PF queues and VMDq pool resources. Incorrect VMVIR programming can force wrong VLAN tags on VF traffic. API declarations must stay synchronized with netdev ops and the implementation, especially around `CONFIG_PCI_IOV` builds.

## Test signals
Build tests should cover configurations with and without `CONFIG_PCI_IOV`. Runtime tests should verify VF count rejection at traffic-class limits, correct VMVIR VLAN/QoS insertion, and netdev VF operation wiring through the declarations in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sysfs.c

## Purpose
`ixgbe_sysfs.c` registers hwmon sysfs attributes for ixgbe thermal sensors. It creates read-only temperature label, input, max, and critical files for sensors reported by MAC thermal-sensor operations.

## Important APIs and functions
The public entry points are `ixgbe_sysfs_init` and `ixgbe_sysfs_exit`, called from ixgbe main driver code. `ixgbe_add_hwmon_attr` builds one `device_attribute` for a selected sensor and type. Show callbacks are `ixgbe_hwmon_show_location`, `ixgbe_hwmon_show_temp`, `ixgbe_hwmon_show_cautionthresh`, and `ixgbe_hwmon_show_maxopthresh`.

## Control flow
Initialization first checks whether `init_thermal_sensor_thresh` exists. It calls that MAC op and exits if no thermal sensors are present or initialization fails. It allocates `struct hwmon_buff` with `devm_kzalloc`, iterates `IXGBE_MAX_SENSORS`, skips sensors with location zero, and adds four read-only attributes for each meaningful sensor. It then registers the group with `devm_hwmon_device_register_with_groups`.

The temperature show callback refreshes sensor data through `get_thermal_sensor_data`, reads the cached temperature, converts degrees to millidegrees, and prints a decimal value. Threshold callbacks print cached caution and maximum operating thresholds in millidegrees. Location prints `locN`.

## State and persistence
The runtime state is `adapter->ixgbe_hwmon_buff`, containing attribute descriptors, names, attribute pointers, group data, and an `n_hwmon` counter. Each attribute points at one `adapter->hw.mac.thermal_sensor_data.sensor[offset]`. Device-managed allocation and registration tie cleanup to the device; `ixgbe_sysfs_del_adapter` is empty and `ixgbe_sysfs_exit` is effectively a stub.

## Dependencies and integration points
The file depends on Linux sysfs, kobject, device, netdevice, and hwmon APIs, plus ixgbe MAC thermal-sensor ops and sensor data structures. It integrates with probe/remove paths and exposes values under the kernel hwmon interface rather than custom netdev attributes.

## Risks and edge cases
The code assumes the hwmon buffer has enough preallocated entries for four attributes per populated sensor. If a MAC reports many sensors but the backing arrays are too small in the struct definition, attributes could overflow. A failure after some attributes are added exits before registration, relying on devm cleanup for allocated memory. The empty delete hook is acceptable for devm-managed hwmon but would be insufficient if non-devm registration were introduced.

## Test signals
Tests should validate no hwmon device appears when thermal ops are absent or report no sensors, all expected `tempN_*` attributes appear for populated sensors, values are in millidegrees, `get_thermal_sensor_data` is called on temperature reads, registration failure propagates an error, and driver remove/unbind cleans up hwmon entries through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_txrx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_txrx_common.h

## Purpose
`ixgbe_txrx_common.h` declares shared transmit/receive helpers used by ixgbe data paths, including XDP, AF_XDP zero-copy, ring enable/disable, interrupt rearming, skb receive processing, and ring statistics updates.

## Important APIs and constants
`IXGBE_XDP_PASS`, `IXGBE_XDP_CONSUMED`, `IXGBE_XDP_TX`, `IXGBE_XDP_REDIR`, and `IXGBE_XDP_EXIT` encode XDP action outcomes used by Rx processing. `IXGBE_TXD_CMD` combines EOP and report-status descriptor command bits for Tx descriptors.

The declared functions include XDP transmit and tail updates (`ixgbe_xmit_xdp_ring`, `ixgbe_xdp_ring_update_tail`, `ixgbe_xdp_ring_update_tail_locked`), skb cleanup and field processing (`ixgbe_cleanup_headers`, `ixgbe_process_skb_fields`, `ixgbe_rx_skb`), queue interrupt rearming (`ixgbe_irq_rearm_queues`), ring disable/enable (`ixgbe_txrx_ring_disable`, `ixgbe_txrx_ring_enable`), AF_XDP pool setup and wakeup, zero-copy Rx/Tx cleanup, and Tx/Rx ring stats aggregation.

## Control flow and integration
This header does not implement logic. It provides common prototypes so split ixgbe Tx/Rx implementation files can share helpers without duplicating declarations. The data path likely calls cleanup and field processing before passing skbs up, uses XDP return bits to decide whether to consume, transmit, redirect, or continue, and uses AF_XDP functions when an XSK pool is bound to a queue.

## State and persistence
No state is stored here. Declared functions operate on runtime structures such as `ixgbe_ring`, `ixgbe_q_vector`, `ixgbe_adapter`, `net_device`, `sk_buff`, `xdp_frame`, and `xsk_buff_pool`. Persistent hardware-visible state affected by implementations includes descriptor rings, tails, queue enable bits, interrupt masks, and per-ring counters.

## Dependencies and integration points
The header expects ixgbe core structures and Linux networking/XDP/AF_XDP types to be visible through including translation units. It connects classic skb networking, XDP fast paths, AF_XDP zero-copy, interrupt moderation/rearm, and statistics accounting.

## Risks and edge cases
Because this header defines shared action bits and prototypes, mismatches with implementation signatures or action semantics can break multiple Tx/Rx variants. XDP and AF_XDP paths are sensitive to ring ownership, memory lifetime, and tail updates; callers need consistent locking and queue state assumptions.

## Test signals
Build coverage should include XDP and AF_XDP enabled configurations. Runtime signals include XDP_PASS/CONSUMED/TX/REDIR correctness, XSK pool bind/unbind and wakeup behavior, zero-copy Rx buffer replenishment, XDP Tx cleanup under NAPI budget, ring disable/enable during queue reconfiguration, interrupt rearming after NAPI, and accurate per-ring packet/byte stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_txrx_common.h -->
