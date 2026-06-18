# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_smn.h

### Purpose
`xgmi_4_0_0_smn.h` defines the SMN address of the XGMI 4.0.0 PCS GOPX16 error-status register. The single exported macro, `smnXGMI0_PCS_GOPX16_PCS_ERROR_STATUS`, is the address anchor used by AMDGPU to read XGMI PCS link error status.

### Important APIs, Types, And Functions
The header exports `smnXGMI0_PCS_GOPX16_PCS_ERROR_STATUS` with value `0x11af0210`. There are no functions or types. Consumers use the macro as an absolute SMN address and derive additional instances by adding fixed offsets.

### Control Flow
No control flow is present in this header. At runtime, `amdgpu_xgmi.c` places the base address into XGMI PCS status register arrays, derives further link addresses with additions such as `+ 0x100000`, `+ 0x500000`, and higher instance offsets, reads those registers through SMN accessors, and decodes fields with `xgmi_4_0_0_sh_mask.h`.

### State, Persistence, And Dependencies
The header contains no mutable state and does not persist data. The referenced hardware register contains the link status. Correct operation depends on the AMDGPU SMN read path, the XGMI IP version selection in `amdgpu_xgmi.c`, and the companion shift/mask header.

### Integration Points
The direct integration point is `amdgpu_xgmi.c`, where the address is used for Vega20 and Arcturus XGMI PCS status arrays. The arrays feed RAS reporting and multi-GPU XGMI hive diagnostics.

### Risks
Address drift is high impact because every decoded field would then come from the wrong hardware location. Derived instance addresses amplify a wrong base address across multiple links. The header is generation-specific; newer XGMI 6.x handling uses local SMN constants and the XGMI 6.1.0 mask header, so broad reuse of this address beyond its intended IP block is risky.

### Test Signals
Signals include compile coverage of XGMI RAS code, SMN register dumps showing `0x11af0210` and derived addresses correspond to PCS error-status registers, correct per-link RAS attribution on multi-link GPUs, and absence of SMN access faults on supported hardware.
