# sources/distributed-fs/ceph-client/include/kunit/of.h

Source read summary: 122 lines, 3506 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/of.h` declares KUnit helpers and macros for applying device-tree overlays, declaring overlay blobs, and registering cleanup for OF node references.

Important APIs, types, and functions: Important exported functions or hooks: `of_node_put_kunit`, `of_overlay_fdt_apply_kunit`. Important types: `device_node`. Important constants/macros: `of_overlay_begin`, `of_overlay_end`, `OF_OVERLAY_DECLARE`, `of_overlay_apply_kunit`.

Control flow: Tests use `OF_OVERLAY_DECLARE`, `of_overlay_apply_kunit()`, or `of_overlay_fdt_apply_kunit()` to install a temporary overlay, then KUnit cleanup removes it and drops OF node references.

State and persistence behavior: Overlay state mutates the live OF tree during a test and must be removed before the next test. Node references are scoped to KUnit cleanup.

Dependencies and integration points: It includes `kunit/test.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Overlay lifetime, duplicate symbols, failed partial applies, and leaked node references can contaminate later tests.

Test signals: Run OF overlay KUnit tests for apply/remove, invalid FDT data, nested overlays, node get/put cleanup, and tests that fail after applying an overlay.
