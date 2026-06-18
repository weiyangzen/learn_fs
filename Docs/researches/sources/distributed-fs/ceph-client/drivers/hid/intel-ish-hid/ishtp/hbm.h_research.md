# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.h

## Purpose
`hbm.h` defines the wire-level ISHTP Host Bus Message protocol used by `hbm.c`, `client.c`, DMA transfer paths, system-state fixed clients, and the ISH firmware loader. It contains opcodes, packed message layouts, timeout/version constants, state enums, and public HBM function declarations.

## Important APIs, types, and functions
Important types include `struct ishtp_msg_hdr`, `struct ishtp_bus_message`, `struct hbm_host_version_request/response`, `struct hbm_host_enum_response`, `struct ishtp_client_properties`, `struct hbm_props_request/response`, connect/disconnect request/response structures, `struct hbm_flow_control`, `struct dma_alloc_notify`, `struct dma_xfer_hbm`, and system-state message structures. `enum ishtp_hbm_state` describes HBM progression from idle to working/stopped. `ishtp_hbm_hdr()` initializes host-bus message headers.

## Control flow and integration points
The header has only the inline header initializer. Its declarations are used by the startup path, interrupt RX path, client connection code, suspend/resume notification code, and loader fixed-client handling. Opcode values drive dispatch in `hbm.c`; packed layouts must match firmware exactly.

## State and persistence behavior
The header defines no storage. It defines protocol state values stored in `struct ishtp_device` and state/status bitfields carried in firmware messages. All state is volatile per runtime session.

## Dependencies
It depends on Linux UUID types and ISHTP forward declarations. Its structures intentionally use fixed-width integer types and `__packed` to match the firmware ABI.

## Risks and edge cases
Any layout, opcode, bit-width, or packing drift breaks firmware compatibility. `struct ishtp_msg_hdr` uses bitfields whose ABI depends on compiler/platform assumptions, so this code is tied to the kernel's supported environment. The DMA and system-state structures include reserved fields that must remain zeroed by senders. Timeout constants directly shape probe and client connect failure behavior.

## Test signals
Protocol ABI tests should validate structure sizes and opcode values, HBM startup against real firmware, DMA transfer descriptor parsing, fixed-client system-state exchange, unsupported version handling, and build coverage for endian/packing warnings.
