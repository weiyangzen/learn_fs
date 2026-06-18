# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_dma_buf.c

## Purpose

`xe_dma_buf.c` is a live KUnit suite for Xe dma-buf export/import behavior. It verifies same-driver imports across combinations of VRAM/system residency, P2P capability, dynamic attachment support, and fake different-device behavior.

## Important APIs, Types, and Functions

- Capability helpers: `p2p_enabled()` and `is_dynamic()`.
- Placement validator: `check_residency()`.
- Main scenario: `xe_test_dmabuf_import_same_driver()`.
- Test parameter table: `test_params` with memory masks, attach ops, and `force_different_devices`.
- Runner/suite: `dma_buf_run_device`, `xe_dma_buf_kunit`, and exported `xe_dma_buf_test_suite`.

## Control Flow

For each live device and parameter set, the test creates a BO with the requested memory mask, exports it with `xe_gem_prime_export`, imports it with `xe_gem_prime_import`, validates the imported BO, checks expected success/failure depending on P2P and dynamic attachment capabilities, evicts exporter state, revalidates importer state, and optionally pins/unpins the dma-buf attachment.

## State and Persistence Behavior

The test mutates BO residency, dma-buf attachment lists, GEM dma-buf backpointers, TTM placement, exporter/importer object references, and runtime PM state. Dynamic attachments are expected to propagate eviction invalidation from exporter to importer.

## Dependencies and Integration Points

It depends on live-device parameter generation, Xe BO/GEM prime export/import, dma-buf attachment ops (`xe_dma_buf_attach_ops` and a no-P2P variant), TTM memory managers, runtime PM, and test-private tagging through `XE_TEST_LIVE_DMA_BUF`.

## Risks and Edge Cases

- P2P behavior is conditional on `CONFIG_PCI_P2PDMA`; expected outcomes change with config.
- Fake different-device behavior avoids same-object import shortcuts and is important for cross-device paths.
- Non-dynamic attachments can reject VRAM pinning without system fallback.
- The test tolerates interrupt-related validation failures but treats unexpected errors as regressions.

## Test Signals

Passing signals include correct import reuse on same device, correct `-EOPNOTSUPP` or `-EINVAL` cases, expected system-memory fallback without P2P, exporter/importer residency synchronization, and successful attachment pinning without unwanted migration.
