<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h

## Purpose
Declares the public Vega10 IH integration symbols for the AMDGPU IP framework and any code that needs the IH function table.

## Important APIs, Types, And Functions
Declares `extern const struct amd_ip_funcs vega10_ih_ip_funcs` and `extern const struct amdgpu_ip_block_version vega10_ih_ip_block`, both defined by `vega10_ih.c`.

## Control Flow
The header contains no executable flow. The AMDGPU device/IP setup code references the declared IP block, then invokes the lifecycle callbacks and IH functions provided by the C file.

## State And Persistence
No state is stored in the header. It exposes symbols that control per-device IH state in `adev->irq` at runtime.

## Dependencies And Integration Points
Consumers need declarations for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. It integrates with ASIC discovery and the interrupt subsystem by linking those symbols.

## Risks And Test Signals
Risk is confined to symbol drift or wrong IP block selection. Compilation validates the declarations; runtime validation comes from interrupt ring initialization and actual GPU interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h -->
