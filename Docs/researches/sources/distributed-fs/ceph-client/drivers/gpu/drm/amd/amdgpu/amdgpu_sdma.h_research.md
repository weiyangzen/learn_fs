## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.h

Purpose: defines common SDMA data structures, IRQ instance IDs, RAS memory IDs, SDMA function callbacks, buffer-copy/fill function table, and public SDMA helper prototypes.

Important APIs and types: `AMDGPU_MAX_SDMA_INSTANCES` caps instances at 16; `enum amdgpu_sdma_irq` enumerates per-instance ECC IRQ indices. `struct amdgpu_sdma_funcs` supplies stop/start/soft-reset kernel queue callbacks. `struct amdgpu_sdma_instance` stores firmware, two rings, burst-NOP, AID/XCC ID, firmware BO, reset mutex, guilty state, and callbacks. `enum amdgpu_sdma_ras_memory_id` names SDMA memory blocks for RAS. `struct amdgpu_sdma` aggregates instances, IRQ sources, masks, page-queue flags, RAS state, dumps, reset support, and CSA info callback. `struct amdgpu_buffer_funcs` exposes SDMA-backed copy/fill emitters used by memory management.

Control flow: the header defines the contracts implemented by `amdgpu_sdma.c` and IP-specific SDMA generations. Macros `amdgpu_emit_copy_buffer` and `amdgpu_emit_fill_buffer` dispatch through `adev->mman.buffer_funcs`.

State and persistence: structures are runtime driver state and hardware command-emission callbacks. Firmware pointers and BOs are kernel resources tied to device lifetime.

Dependencies and integration points: includes `amdgpu_ras.h` and references rings, devices, IRQs, firmware, and buffer manager code. Used by SDMA IP blocks, TTM migration/fill code, RAS, reset, and scheduler integration.

Risks: the `union` of `aid_id/xcc_id` assumes mutually exclusive interpretation by ASIC family. Function callbacks are optional in some paths but reset logic depends on them for per-engine reset. Shared ring/page queue fields must be initialized consistently with `has_page_queue`.

Test signals: compile coverage for IP callbacks, SDMA ring init/tests, buffer copy/fill migration tests, RAS block tests, and reset callback coverage.
