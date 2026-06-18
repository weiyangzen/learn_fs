# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.h

Purpose: declarations and data structures for KUnit mock TTM resource managers.

Important APIs and types: `struct ttm_mock_manager` embeds `struct ttm_resource_manager`, a `gpu_buddy` allocator, a `default_page_size`, and a mutex protecting mock BO allocations. `struct ttm_mock_resource` embeds `struct ttm_resource`, a list of allocated buddy blocks, and allocation flags. The header declares manager initialization and teardown functions for normal, bad, and busy managers.

Control flow and state: implementation consumers create managers for arbitrary test memory types, normally `TTM_PL_VRAM`, `TTM_PL_TT`, `TTM_PL_MOCK1`, or `TTM_PL_MOCK2`. Resources record buddy block lists so free paths can return exact allocations. Bad and busy managers do not use `ttm_mock_resource`; they operate through a bare `ttm_resource_manager`.

Dependencies and integration: depends on `linux/gpu_buddy.h` and TTM resource/device declarations supplied by including translation units. Integrated by validation tests and any KUnit path that needs a resource manager more realistic than the system manager.

Risks and test signals: structure layout must match the `container_of()` conversions in `ttm_mock_manager.c`. Missing or mismatched teardown declarations would leave managers registered in the device and poison later tests.
