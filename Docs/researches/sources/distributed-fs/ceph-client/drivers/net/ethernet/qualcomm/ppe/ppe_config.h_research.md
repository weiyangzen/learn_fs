<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h

## Purpose
`ppe_config.h` publishes PPE configuration constants, enums, data structures, and helper prototypes used to configure scheduler, queue, service-code, counter, RSS, and ring-mapping behavior.

## Important APIs, Types, and Data
- Queue base constants define destination-port, CPU-code, and service-code mapping regions.
- RSS constants define IPv4/IPv6 modes, tuple counts, IP mix length, and ring-to-queue bitmap size.
- `enum ppe_scheduler_frame_mode`, `struct ppe_scheduler_cfg`, and `enum ppe_resource_type` describe scheduler inputs and resources.
- `struct ppe_queue_ucast_dest` describes the selector used for unicast queue base lookup.
- Service-code bypass enums split ingress, egress, counter, and tunnel bypass bitmaps; `struct ppe_sc_bypass` stores them with `DECLARE_BITMAP()`.
- `struct ppe_sc_cfg` describes service-code destination, bypass, next-code, and EIP action fields.
- `enum ppe_action_type` defines forward/drop/copy/redirect action values.
- `struct ppe_rss_hash_cfg` describes RSS mask, fragment behavior, seed, mix fields, and final mix selectors.
- Function prototypes expose the configuration entry points implemented in `ppe_config.c`.

## Control Flow
No executable flow exists. The header establishes the contract for caller-supplied values that are later encoded into hardware registers.

## State and Persistence
Structures are caller-owned until encoded into hardware. Bitmaps are embedded in `struct ppe_sc_cfg`; RSS and scheduler configs are passed by value.

## Dependencies and Integration Points
Includes Linux types and `ppe.h`. It is consumed by PPE hardware config and debugfs, and it is the public internal API for future PPE users in the Qualcomm Ethernet stack.

## Risks and Edge Cases
- Enum values are hardware bit positions; reordering would change register encodings.
- Bitmap sizes deliberately exclude unspecified hardware gaps but preserve numeric holes, so callers must use the named enums.
- Several prototypes accept raw integer IDs without type-safe range encoding.
- `PPE_RING_TO_QUEUE_BITMAP_WORD_CNT` assumes 300 queues represented by ten 32-bit words.

## Test Signals
Build coverage catches struct/prototype drift. Unit or hardware tests should verify service-code bitmaps, resource IDs, RSS tuple arrays, and queue bitmap width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h -->
