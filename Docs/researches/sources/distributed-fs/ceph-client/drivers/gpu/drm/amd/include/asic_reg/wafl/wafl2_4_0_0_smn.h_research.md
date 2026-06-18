# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_smn.h

### Purpose
`wafl2_4_0_0_smn.h` defines the SMN address for the WAFL 2.4.0.0 PCS GOPX1 error-status register used by AMDGPU XGMI/WAFL RAS handling. Its single exported address, `smnPCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS`, points at `0x11cf0210`.

### Important APIs, Types, And Functions
The only functional export is the `smnPCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS` macro. It is consumed as a raw SMN address, not as a SOC15 offset/base-index pair. There are no C types, functions, structs, or inline helpers.

### Control Flow
The header has no runtime control flow. Runtime code in `amdgpu_xgmi.c` places this base address and a second instance at base plus `0x100000` into WAFL PCS status arrays. XGMI RAS logic later walks those arrays, reads the status registers, and decodes the status bits with `wafl2_4_0_0_sh_mask.h`.

### State, Persistence, And Dependencies
No software state is stored. The addressed hardware register contains live or sticky WAFL PCS status. The header depends on the SMN access path used by AMDGPU and on exact pairing with the matching shift/mask header; the address has meaning only for ASIC generations whose WAFL block matches this generated map.

### Integration Points
`amdgpu_xgmi.c` includes this file for Vega20 and Arcturus WAFL status arrays. Those arrays integrate with XGMI hive management and RAS error reporting by giving the driver the addresses of the per-link WAFL PCS status registers.

### Risks
An incorrect SMN address sends diagnostics to the wrong register, which can produce false clean status, false link errors, or reads of unrelated hardware state. Instance addressing is derived by arithmetic on this base, so the base must stay aligned with the documented WAFL register aperture. The similarly named Aldebaran WAFL constants are locally defined in `amdgpu_xgmi.c`, so mixing the generated 2.4.0.0 address with newer layouts is a concrete maintenance risk.

### Test Signals
Signals include compile coverage of `amdgpu_xgmi.c`, successful SMN reads from `0x11cf0210` and `0x11df0210` on supported hardware, RAS output that reports WAFL PCS errors only on the expected links, and hardware register dumps matching the generated address map.
