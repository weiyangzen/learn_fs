# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.h

Purpose: SI interrupt handler block declaration header.

Important APIs, types, and functions: declares `extern const struct amdgpu_ip_block_version si_ih_ip_block`.

Control flow: no header runtime flow. The descriptor lets SI common add IH to the amdgpu IP block list.

State and persistence: no state here; `si_ih.c` owns IH ring and interrupt state through `adev->irq`.

Dependencies and integration points: included by `si.c` and any SI code that needs the IH IP descriptor.

Risks and test signals: build linkage is the main risk. Runtime signal is successful IRQ setup and interrupt vector decoding on SI devices.
