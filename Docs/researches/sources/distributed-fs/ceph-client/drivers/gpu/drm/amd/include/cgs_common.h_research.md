# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cgs_common.h

## Purpose

`cgs_common.h` defines the common services interface used by AMDGPU subsystems that need hardware access without depending directly on the full `amdgpu_device` implementation. CGS exposes an opaque `struct cgs_device`, a vtable of MMIO/indirect-register/firmware-info operations, field manipulation macros, and convenience wrappers. It is used by PowerPlay, ACP, Display, and related components as a narrow adapter layer over AMDGPU register and firmware services.

## Important APIs, Types, and Macros

Core types:

- `struct cgs_device` contains `const struct cgs_ops *ops` and is intended to be embedded at the start of a driver-private structure.
- `struct cgs_ops` provides `read_register`, `write_register`, `read_ind_register`, `write_ind_register`, and `get_firmware_info`.
- `struct cgs_firmware_info` returns firmware versioning, image size, MC address, SMC start address, kernel pointer, and kicker status.
- `enum cgs_ind_reg` names indirect spaces: PCIE, SMC, UVD context, DIDT, GC CAC, SE CAC, and audio endpoint.
- `enum cgs_ucode_id` names firmware classes: SMU, SMU SK, SDMA0/1, CP CE/PFP/ME/MEC/MEC JT, GMCON RENG, RLC G, storage, and maximum sentinel.

Register access macros form generated shift/mask symbol names, extract and update bitfields, perform read-modify-write direct and indirect register updates, and dispatch through `CGS_CALL` wrappers such as `cgs_read_register`, `cgs_write_register`, `cgs_read_ind_register`, `cgs_write_ind_register`, and `cgs_get_firmware_info`.

## Control Flow

The header's control flow is macro-based dispatch. A subsystem receives an opaque `struct cgs_device *`; a wrapper such as `cgs_read_register(dev, offset)` expands to `CGS_CALL(read_register, dev, offset)`; `CGS_CALL` casts the pointer and calls the selected function pointer from `ops`. Field write helpers perform a read-modify-write sequence using direct MMIO or a selected indirect register space. Firmware queries call `get_firmware_info` with a `cgs_ucode_id` and fill `struct cgs_firmware_info`.

The concrete implementation in this tree is `amdgpu_cgs.c`, where `struct amdgpu_cgs_device` embeds `struct cgs_device` and forwards operations to AMDGPU register and firmware helpers.

## State and Persistence Behavior

The header defines no storage. Runtime state is held by the concrete object embedding `struct cgs_device` and by hardware. Register reads/writes affect GPU MMIO state immediately. Indirect operations affect the selected indirect register space. Firmware info points to loaded firmware metadata and may include a CPU pointer to firmware image data. The `ops` pointer must remain valid for the lifetime of every user of the CGS device.

## Dependencies

The header includes `amd_shared.h` for shared AMD types and depends on fixed-width integer and boolean definitions from the kernel build environment. It expects generated register headers to define `mm<reg>`, `ix<reg>`, `<reg>__<field>__SHIFT`, and `<reg>__<field>_MASK` symbols used by the field macros. `CGS_OS_CALL` assumes an `os_ops` member exists in an OS-specific extension, although `struct cgs_device` here only defines `ops`.

## Integration Points

Representative users include `amdgpu/amdgpu_cgs.c`, `amdgpu/amdgpu_acp.c`, `acp/acp_hw.c`, `display/amdgpu_dm/*`, Display Core initialization, and PowerPlay hwmgr/smumgr code such as `vega10_hwmgr.c`, `vega20_processpptables.c`, and `smu7_hwmgr.c`.

## Risks and Edge Cases

- `ops` is not checked for NULL by wrapper macros. Callers must ensure the CGS device is fully initialized and not destroyed.
- Field write macros perform read-modify-write without locking. Concurrent access to the same register can lose updates unless higher layers serialize.
- `CGS_WREG32_FIELD` and `CGS_WREG32_FIELD_IND` shift `val` but do not explicitly mask it after shifting. Out-of-range field values can leak into adjacent bits.
- Direct and indirect offsets are compile-time macro conventions. Passing a generated symbol from the wrong IP/version header can access the wrong register.
- `CGS_OS_CALL` references `os_ops`, which is not present in the common struct definition. It must only be used with an OS-specific compatible extension.
- Firmware info pointers and MC addresses are only valid according to the owning firmware loader's lifetime rules.

## Test Signals

Build tests across AMDGPU, Display, ACP, and PowerPlay catch vtable and macro signature mismatches. Register read/write smoke tests through CGS should match direct AMDGPU helper behavior. Field macro tests should validate `CGS_REG_SET_FIELD`/`GET_FIELD` for representative generated masks and boundary values. Firmware loading tests should verify every `cgs_ucode_id` used by a platform returns expected version, size, address, and pointer data or a clean error. Concurrency-sensitive tests around power management and display mode setting can expose read-modify-write races.
