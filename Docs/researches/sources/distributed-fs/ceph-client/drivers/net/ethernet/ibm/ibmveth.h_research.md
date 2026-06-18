
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.h

## Purpose
`ibmveth.h` defines the firmware/hypervisor interface constants, hcall wrappers, buffer-pool defaults, adapter state structures, TX/RX descriptor formats, and RX queue entry bits for the IBM virtual Ethernet driver.

## Important APIs, Types, and Functions
Hcall wrappers/macros include `h_register_logical_lan()`, `h_free_logical_lan()`, `h_add_logical_lan_buffer()`, `h_add_logical_lan_buffers()`, `h_send_logical_lan()`, `h_illan_attributes()`, `h_multicast_ctrl()`, and `h_change_logical_lan_mac()`. Capability bits include checksum, large send, active trunk, padded packet checksum, and RX multi-buffer support. Defaults define five RX pools, pool sizes/counts/active states, CMO pool counts, maximum TX buffer size, max/default queue counts, and max RX descriptors per hcall. Core structures are `struct ibmveth_buff_pool`, `struct ibmveth_rx_q`, `struct ibmveth_adapter`, `struct ibmveth_buf_desc_fields`, `union ibmveth_buf_desc`, and `struct ibmveth_rx_q_entry`.

## Control Flow
The header’s wrappers are called throughout `ibmveth.c` for logical LAN registration, buffer submission, packet send, attribute negotiation, multicast filtering, and MAC changes. Descriptor and RX queue bit definitions drive TX descriptor construction and RX poll parsing. Pool default arrays are used at probe to initialize per-adapter pool kobjects and runtime replenish behavior.

## State and Persistence
`struct ibmveth_adapter` is all volatile per-device state. RX pool arrays contain dynamic allocation pointers and atomic available counters. The descriptor union intentionally handles endian ordering because descriptors are passed as register-sized values to hypervisor calls. No data persists outside runtime.

## Dependencies and Integration Points
The file depends on PowerPC PAPR hypervisor call APIs and VIO conventions. It is tightly coupled to PHYP’s logical LAN ABI, including correlator layout, multicast control command bits, and `H_SEND_LOGICAL_LAN` argument conventions with optional MSS/large-send support.

## Risks
Static pool arrays in a header would be problematic if included by multiple C files, but this header is intended for the single implementation. Endian-specific descriptor field ordering is critical. `h_send_logical_lan()` has two call shapes depending on firmware large-send support; argument mismatch would corrupt sends. Pool and buffer size constants gate MTU and DMA entitlement calculations.

## Test Signals
Compile coverage on big-endian and little-endian PowerPC configurations, successful firmware capability negotiation, descriptor flag correctness in TX/RX traces, CMO desired-DMA calculations, sysfs pool defaults, and KUnit tests that exercise pool/queue structures validate this header.
