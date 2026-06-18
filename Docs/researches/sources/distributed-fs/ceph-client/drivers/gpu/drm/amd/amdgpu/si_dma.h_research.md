# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.h

Purpose: SI SDMA block declaration header.

Important APIs, types, and functions: declares `extern const struct amdgpu_ip_block_version si_dma_ip_block`, the IP block descriptor consumed by `si_set_ip_blocks()`.

Control flow: no runtime flow in the header. The descriptor points amdgpu core at the SDMA lifecycle callbacks in `si_dma.c`.

State and persistence: no state is stored in the header; runtime state is in `adev->sdma`, rings, writeback memory, and SDMA registers.

Dependencies and integration points: included by `si.c` to add the SDMA block to the device IP list and by any SI code needing the descriptor.

Risks and test signals: build errors catch declaration drift. Runtime signal is that SI devices register and initialize `AMD_IP_BLOCK_TYPE_SDMA` successfully.
