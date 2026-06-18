# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/common.h

## Purpose
Private SCMI core header shared by bus, driver, transports, protocol implementations, raw mode, and notification code. It defines common limits, error mapping, message header packing, transfer lookup helpers, bus/device APIs, transport descriptors, shared-memory/message datagram operations, debug counters, and transport-driver scaffolding.

## APIs, Types, And Functions
Important definitions include `SCMI_MAX_CHANNELS`, `SCMI_MAX_RESPONSE_TIMEOUT`, SCMI firmware-to-Linux error mapping through `scmi_to_linux_errno()`, message header masks and `pack_scmi_header()`/`unpack_scmi_header()`, `XFER_FIND()`, `struct scmi_chan_info`, `struct scmi_transport_ops`, `struct scmi_desc`, `struct scmi_debug_info`, `struct scmi_shared_mem_operations`, `struct scmi_message_operations`, `struct scmi_transport_core_operations`, `struct scmi_transport`, and `DEFINE_SCMI_TRANSPORT_DRIVER()`.

## Control Flow
Inline helpers determine whether polling is required, whether a transport is polling-capable, and whether polling is enabled. Header packing/unpacking defines the common transfer format. The transport-driver macro creates a platform transport probe that allocates an `arm-scmi` platform device, attaches copied transport descriptor data, parents it to the supplier, and registers automatic cleanup.

## State, Persistence, And Dependencies
The header declares but does not own most state. Structures defined here are embedded in runtime SCMI instances, channels, transports, and debugfs data. Optional debug counters increment/decrement atomically only when `CONFIG_ARM_SCMI_DEBUG_COUNTERS` is enabled. Dependencies include completion, device core, hash tables, lists, refcounts, spinlocks, public SCMI protocol definitions, notifications, and protocol IDs.

## Integration Points
Nearly every SCMI implementation file includes this header. It connects protocol registration to bus device creation, main driver transfer handling to transports, and shared-memory/message transport implementations to the core RX/TX callbacks.

## Risks And Test Signals
Risks are broad because this is a shared contract: header bitfield changes can break firmware ABI, transport descriptor changes can break every transport, and macro changes can alter probe ordering or cleanup. Signals are full SCMI build coverage, transport-specific boot tests, message header round trips, debug counter sanity checks, raw-mode compile coverage, and sparse/static analysis for structure contract drift.
