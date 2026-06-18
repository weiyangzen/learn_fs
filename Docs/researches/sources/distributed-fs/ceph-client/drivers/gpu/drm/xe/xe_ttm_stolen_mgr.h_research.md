# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.h

Purpose: Declares the stolen-memory manager interface used by Xe memory-management and BO mapping code.

Important APIs/types/functions: Declares `xe_ttm_stolen_mgr_init`, `xe_ttm_stolen_io_mem_reserve`, `xe_ttm_stolen_cpu_access_needs_ggtt`, `xe_ttm_stolen_io_offset`, and `xe_ttm_stolen_gpu_offset`, with forward declarations for `ttm_resource`, `xe_bo`, and `xe_device`.

Control flow: Consumers initialize stolen memory during device memory-manager setup, ask whether CPU access must be GGTT-mediated, reserve TTM bus mappings for stolen resources, and convert BO/resource offsets into CPU or GPU-visible addresses.

State and persistence behavior: The header owns no state. Its API exposes access to the hidden manager state initialized in the C file.

Dependencies and integration points: Included by BO mapping, TTM manager setup, and stolen-memory placement paths. It intentionally hides `struct xe_ttm_stolen_mgr` internals.

Risks: Callers must only use offset/reserve helpers after successful manager initialization and for `XE_PL_STOLEN` resources. Incorrect use on non-stolen BOs would produce meaningless offsets.

Test signals: Compile coverage of all callers and runtime stolen-memory allocation/mapping tests on platforms with and without stolen support.
