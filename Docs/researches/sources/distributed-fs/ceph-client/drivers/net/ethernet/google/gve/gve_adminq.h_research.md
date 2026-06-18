# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.h

## Purpose
Defines the gVNIC admin queue ABI shared between the driver and device firmware. It enumerates opcodes/status codes, device descriptor/options, driver capability bits, command payload structures, flow/RSS/PTYPE/stat/timestamp formats, the 64-byte admin command union, and adminq function prototypes.

## Important APIs and Types
Important enums include admin opcodes, extended opcodes, status codes, device option ids, supported feature masks, driver capabilities, set-driver-parameter types, stat names, L3/L4 PTYPE values, flow config/query opcodes, flow types, and RSS hash types. Structures are guarded by `static_assert()` size checks to preserve ABI layout. The union `gve_adminq_command` is exactly 64 bytes and embeds all inline command payloads plus the extended command wrapper.

## Control Flow and Integration
`gve_adminq.c` fills these structures, converts fields to big endian, and submits them through the admin queue. Device descriptor and option structures drive probe-time feature negotiation; create/destroy queue commands bind driver-allocated rings and queue resources to device queues; report/query commands hand coherent DMA buffers to the device for output.

## State and Persistence
This header defines wire-format state, not runtime storage. Persistent driver state derived from it is stored in `gve_priv`: queue format, descriptor counts, max pages, RSS sizes, feature flags, flow limits, link speed, timestamp support, and admin counters.

## Dependencies and Risks
Depends on Linux fixed-width big-endian types, Ethernet address definitions, and `struct gve_flow_spec` from `gve.h` for flow-rule payloads. Risks are ABI drift, size/alignment changes, missing endian conversions, unsupported option-length compatibility, and command union overflow. Test signals include compile-time static asserts, admin command traces/status injection, probe against devices with old/new option lengths, and exercising every public adminq command path.
