# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_config.h Research

## Purpose
`octep_config.h` defines static defaults, access macros, and configuration structures for Octeon EP queue, SR-IOV, MSI-X, control mailbox, firmware, heartbeat, offload, and MTU settings.

## Important APIs, Types, And Functions
Constants define IQ/OQ descriptor counts, 32/64-byte instruction modes, doorbell batching, interrupt thresholds, RX buffer size and refill threshold, queue wake threshold, MTU defaults, MSI-X name length, RX watermark, and firmware heartbeat defaults. `CFG_GET_*` macros provide shorthand accessors for nested fields in `struct octep_config`.

The main types are `struct octep_iq_config`, `struct octep_oq_config`, `struct octep_pf_ring_config`, `struct octep_sriov_config`, `struct octep_msix_config`, `struct octep_ctrl_mbox_config`, `struct octep_fw_info`, and aggregate `struct octep_config`.

## Control Flow
This header implements no control flow. Chip-specific PF setup files populate `struct octep_config` from hardware CSRs and defaults, while common queue, interrupt, mailbox, ethtool, and control-plane code reads it through direct fields or accessor macros.

## State, Persistence, And Dependencies
The configuration object is persistent per `struct octep_device` during driver lifetime. It captures maximum and active ring counts, SR-IOV limits, queue sizes, coalescing policy, BAR memory address for the control mailbox, firmware-provided interface info, offload flags, and heartbeat policy. It depends on networking constants such as `ETH_MIN_MTU`, `IFNAMSIZ`, `SKB_WITH_OVERHEAD()`, and `PAGE_SIZE`.

## Integration Points
CN9K/CNXK setup fills the configuration. Tx/Rx ring allocation and queue programming use IQ/OQ values. Interrupt allocation uses MSI-X counts and names. Control net initialization uses `CFG_GET_CTRL_MBOX_MEM_ADDR()`. Ettool channel reporting uses active/max IO rings. Firmware info returned over the control net protocol is stored in `fw_info`.

## Risks
Many macros are simple field accessors, so they do not validate null pointers or bounds. Queue descriptor counts are fixed at 1024 and documented as power-of-two; changing them affects ring wrap logic. `OCTEP_OQ_BUF_SIZE` depends on page-size SKB overhead and may vary by architecture. Active counts are populated from hardware and used in loops and interrupt masks, so invalid firmware/CSR values can propagate widely.

## Test Signals
Build on architectures with different page sizes, validate active ring counts against allocated arrays and interrupt masks, verify MTU boundary behavior, check RX refill and queue wake thresholds under traffic, confirm heartbeat defaults are overridden when firmware info is fetched, and test offload feature negotiation through `struct octep_fw_info`.
