<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_key.h -->
# sources/distributed-fs/ceph-client/include/linux/static_key.h

Purpose: Compatibility include for static keys that forwards to the jump-label implementation.

Important APIs/types/functions: No local APIs; all static key/static branch definitions come from `linux/jump_label.h`.

Control flow: Single include.

State and persistence behavior: No local state; jump-label static keys manage state elsewhere.

Dependencies: `linux/jump_label.h`.

Integration points: Source compatibility for code including `static_key.h`.

Risks: All behavior and build requirements are inherited from jump labels.

Test signals: Compile-only tests for code including `static_key.h` and using static branch APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_key.h -->
