# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.h

## Purpose
`fjes_hw.h` defines the hardware-facing data model for FJES: endpoint buffer layout, ring sizing macros, command request/response formats, shared status, per-endpoint statistics, trace buffer layout, hardware resource state, and the public low-level API used by `fjes_main.c`, ethtool, debugfs, and tracepoints.

## Important APIs and Types
Important macros include endpoint buffer sizes, ring helpers (`EP_RING_INDEX`, `EP_RING_FULL`, `EP_RING_EMPTY`), MTU/frame conversions, command buffer length formulas, command timeouts, zoning constants, TX/RX status bits, and debug buffer sizes. Core types are `struct esmem_frame`, `enum ep_partner_status`, `struct fjes_device_shared_info`, `union fjes_device_command_req`, `union fjes_device_command_res`, `enum fjes_dev_command_request_type`, `struct fjes_device_command_param`, `enum fjes_dev_command_response_e`, `union ep_buffer_info`, `struct fjes_drv_ep_stats`, `struct ep_share_mem_info`, `struct es_device_trace`, `struct fjes_hw_info`, and `struct fjes_hw`.

## Control Flow
The header itself has no executable flow, but its structures define the control protocol. `fjes_hw.c` writes command request unions, device firmware fills response unions and shared endpoint status, TX writes `esmem_frame` entries into a peer's shared ring, RX consumes peer-written frames, and endpoint status bits coordinate MTU changes, polling, and stop handshakes.

## State, Dependencies, and Integration
`struct fjes_hw_info` owns command buffers, shared status, trace memory, locks, and share bitmaps. `struct fjes_hw` embeds runtime hardware resource identifiers, MMIO base, endpoint memory, stop bits, work items, and debug mode. The header depends on Linux netdevice/VLAN/vmalloc primitives and `fjes_regs.h`.

## Risks and Test Signals
Risks are ABI/layout drift with device firmware, endian assumptions in command unions, ring macro off-by-one behavior, and bitmask size limits if `max_epid` exceeds an `unsigned long`. Tests should validate structure sizes/offsets against firmware expectations, ring helper behavior for wrap/full/empty, MTU-to-frame calculations, command buffer length calculations, and status-bit transitions for stop and MTU changes.
