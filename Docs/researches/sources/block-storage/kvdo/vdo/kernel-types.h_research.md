# File Research: sources/block-storage/kvdo/vdo/kernel-types.h

Central kernel-facing VDO type aliases, enums, priorities, forward declarations, and a zoned physical block helper.

Key responsibilities:
- Defines small-width types such as `compressed_fragment_count_t`, `page_size_t`, `thread_count_t`, `thread_id_t`, and `vio_count_t`.
- Defines `VDO_INVALID_THREAD_ID`.
- Defines data VIO operation bit flags and masks.
- Defines `enum vio_type` for data and metadata/statistics categories.
- Provides inline helpers to classify data versus metadata VIO types.
- Defines completion priority constants for bio, CPU, UDS, and default queues.
- Defines `enum vio_priority` and `enum vdo_zone_type`.
- Forward-declares many core VDO structures.
- Defines `struct zoned_pbn` containing PBN, mapping state, and physical zone pointer.

Dependencies:
- Includes `types.h` and Linux version headers.

Notable risks:
- Many core subsystems depend on these enum numeric values for queue priority and instrumentation.
- Thread IDs are `uint8_t`, so thread-count assumptions are bounded by that representation.
