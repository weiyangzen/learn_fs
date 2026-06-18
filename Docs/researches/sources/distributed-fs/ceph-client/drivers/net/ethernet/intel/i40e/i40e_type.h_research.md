# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_type.h

## Purpose

`i40e_type.h` is the core hardware type and descriptor definition header for the i40e driver. It defines device limits, capability bits, link/PHY/MAC/bus/NVM/DCB structures, the central `struct i40e_hw`, Rx and Tx descriptor layouts, descriptor bit fields, Flow Director programming descriptor fields, switch/VSI/VEB context structures, hardware statistics structures, NVM shadow RAM constants, filter control sizes, reset types, RSS/input-set masks, and Dynamic Device Personalization package structures.

## Important APIs, Types, and Macros

Top-level limits include queue-pair, VF VSI, chained Rx buffer, UDP offload port, NVM timeout, and PHY timeout constants. `I40E_DESC_UNUSED()` is the shared ring-space macro used by Tx/Rx code. Hardware identity and link types include `enum i40e_mac_type`, `enum i40e_media_type`, `enum i40e_fc_mode`, `enum i40e_vsi_type`, and `enum i40e_queue_type`. Link and PHY state is represented by `struct i40e_link_status` and `struct i40e_phy_info`, with PHY capability bit macros for SGMII, BASE-KX/KR/CR/SR/LR/T, AOC/ACC, 25G variants with the documented offset, and 2.5G/5G BASE-T.

`struct i40e_hw_capabilities` records firmware-discovered capabilities such as switch mode, management protocols, SR-IOV, VMDQ, EVB, DCB, FCoE, iSCSI, Flex10, security/update restrictions, PTP, Flow Director counts, RSS table sizes, GPIO LED/SDP capabilities, queue/vector counts, DCB traffic classes, and write-protected CSR bits. `enum i40e_hw_flags` maps driver capability bits used by `hw.caps`. `struct i40e_hw` is the main hardware object: it contains MMIO base, PHY/MAC/bus/NVM/FC substructures, PCI IDs, capabilities, Flow Director shared count, PF/main VSI identifiers, partition data, AdminQ state, NVM update state, HMC state, DCBX configs, capability bitmap, switch tags, and debug state.

Descriptor definitions include `union i40e_16byte_rx_desc`, `union i40e_32byte_rx_desc`, `struct i40e_tx_desc`, `struct i40e_tx_context_desc`, and `struct i40e_filter_program_desc`. Associated enums and masks define Rx status bits, filter-status values, error bits, PTYPE, packet length, programming-status fields, Tx descriptor dtype values, Tx command bits, Tx length offset fields, Tx context command/tunnel fields, and Flow Director filter programming destination/status/command/count fields. Other major groups include `struct i40e_vsi_context`, `struct i40e_veb_context`, `struct i40e_eth_stats`, `struct i40e_veb_tc_stats`, `struct i40e_hw_port_stats`, filter control settings, LLDP variables, alternate RAM offsets, RSS/input-set masks, and DDP package/segment/profile section structures.

## Control Flow

This header is declarative, but it controls runtime behavior by defining the exact memory layouts and bit positions used by fast-path and AdminQ code. Rx polling reads `union i40e_rx_desc::wb.qword1.status_error_len` and extracts status, error, packet type, length, timestamp, VLAN, RSS, and programming status fields using these masks. Tx code writes `struct i40e_tx_desc::buffer_addr` and `cmd_type_offset_bsz` using these command/offset/size/tag shifts, writes context descriptors for TSO/timestamp/tunnel offload, and writes filter programming descriptors for Flow Director sideband and ATR rules. Admin/control-plane code stores firmware-reported capabilities in `struct i40e_hw` and interprets NVM, DCBX, switch, filter-control, and DDP structures with these definitions.

## State and Persistence Behavior

The file defines structures that hold both volatile runtime state and cached firmware/hardware state. `struct i40e_hw` persists for the PCI function lifetime and is refreshed across resets and AdminQ operations. NVM update fields persist during multi-step NVM transactions. Link status, capability bitmaps, DCBX configs, HMC state, and firmware counts are in-memory reflections of hardware or firmware state. Descriptor structures are DMA-visible and persist only while queues are active. NVM/shadow RAM constants refer to nonvolatile device storage, but this header only defines offsets and command shapes; actual persistence is performed by AdminQ/NVM code elsewhere.

## Dependencies and Integration Points

The header includes UAPI Ethernet definitions plus `i40e_adminq.h` and `i40e_hmc.h`, and it is included by most i40e modules. It integrates with firmware AdminQ command handling, queue setup, packet I/O fast paths, Flow Director, RSS, DCB, PTP, NVM update, DDP profile loading, switch/VSI/VEB management, and ethtool statistics. The bit definitions must match the Intel X710/XL710/X722 hardware specification and the firmware ABI.

## Risks and Edge Cases

Descriptor layouts and bit masks are ABI-like contracts with hardware; incorrect shifts, widths, endian conversions, or structure assumptions can cause silent packet corruption, lost checksum offloads, wrong RSS hashes, broken Flow Director programming, or DMA into invalid buffers. `I40E_DESC_UNUSED()` assumes producer/consumer indices are maintained with one empty slot. `I40E_CAP_PHY_TYPE_25GBASE_*` uses an explicit offset because bit 31 is unused while the AdminQ enum has no gap; code that maps PHY enum values to capability bits must preserve this exception. Capability bits in `struct i40e_hw::caps` must be populated before feature decisions such as RSS ptype expansion, writeback-on-ITR, FEC, PTP, or DCB. Flexible-array DDP/package structures require bounds checking by consumers. Several stats fields are hardware counter mirrors and can wrap or require delta accounting elsewhere.

## Test Signals

Validation signals include successful compile of all descriptor and AdminQ users, queue setup with correct descriptor sizes, packet Rx metadata extraction for VLAN/RSS/checksum/timestamp, Tx offload correctness for IPv4/IPv6/UDP/TCP/SCTP/TSO/tunnels, Flow Director add/remove/ATR descriptor programming, firmware capability parsing across X710/XL710/X722 devices, DCBX configuration import/export, NVM update command shape validation, DDP package parsing with malformed size tests, and ethtool statistics matching hardware counters after wrap-aware updates.
