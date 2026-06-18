# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.h

Purpose: exports the CIK SDMA IP block descriptor.

Important API: declares `extern const struct amdgpu_ip_block_version cik_sdma_ip_block`, used by CIK common setup to register the SDMA block for each supported CIK ASIC.

Control flow: no implementation. `cik_set_ip_blocks()` consumes this symbol after selecting the appropriate GFX block and before SMU/display/video blocks.

State and persistence: stateless header; the referenced block owns firmware, rings, interrupts, VM PTE callbacks, and buffer-function state when initialized.

Dependencies and integration points: requires AMDGPU IP block type definitions from includers. Integrates `cik_sdma.c` with ASIC IP block assembly in `cik.c`.

Risks: declaration/definition drift breaks link. IP block ordering must ensure common/GMC/IH prerequisites are available before SDMA initialization and interrupt use.

Test signals: build/link success and runtime IP block list showing SDMA block for Bonaire/Hawaii/Kaveri/Kabini/Mullins.
