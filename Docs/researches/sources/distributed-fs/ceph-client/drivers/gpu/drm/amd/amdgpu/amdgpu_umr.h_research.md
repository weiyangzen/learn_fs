<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h

## Purpose
`amdgpu_umr.h` defines debugfs ioctl ABI structures for UMR-style register, SRBM/GRBM, and GPR/wave access. It is a small shared header for debug tooling state passed through debugfs file operations.

## Important APIs, Types, And Functions
`struct amdgpu_debugfs_regs2_iocdata` carries register access state: whether SRBM/GRBM selection is active, page-lock behavior, GRBM SE/SH/instance, and SRBM ME/pipe/queue/VMID. `struct amdgpu_debugfs_regs2_iocdata_v2` adds `xcc_id` for multi-XCC devices. `struct amdgpu_debugfs_gprwave_iocdata` selects GPR or wave reads by SE/SH/CU/wave/SIMD/XCC and per-thread VGPR/SGPR index. File-private state structs pair an `amdgpu_device`, a mutex, and the current selector data. The `_IOWR` macros define debugfs ioctl commands for setting register and GPR/wave state.

## Control Flow
Debugfs open paths allocate state, ioctl handlers copy one of these structures from userspace, and read/write handlers use the stored selector to choose register addressing mode or wave/GPR target. This header does not implement behavior; it defines the shared ABI contract for those handlers.

## State And Persistence
State is per debugfs file handle. The mutex in each data struct serializes ioctl state updates with subsequent accesses. No persistent device state is changed by the declarations themselves, though the selected state can affect later debugfs reads and writes through the same file descriptor.

## Dependencies And Integration Points
The header depends on Linux ioctl encoding and AMDGPU device definitions included by consumers. It integrates with AMDGPU debugfs register access, GRBM/SRBM selection, multi-XCC debug support, and user-space UMR tooling.

## Risks
Because this is debugfs ABI, structure layout changes can break tools. IOCTL command numbering must remain stable. Consumers must validate selector fields against hardware topology and privilege expectations; this header alone does not constrain ranges. The v1/v2 register state split requires handlers to initialize `xcc_id` safely when old ioctls are used.

## Test Signals
Run UMR/debugfs register access with v1 and v2 state ioctls, multi-XCC selector coverage, invalid selector rejection in consumers, and GPR/wave reads across representative GFX generations. ABI-size checks help protect userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h -->
