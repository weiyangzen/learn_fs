# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vf_error.h

## Purpose

`amdgpu_vf_error.h` declares the VF error ABI constants and functions used by SR-IOV virtual functions to report driver/GPU initialization and reset errors back to the host-side GIM/PF component.

## Important APIs And Types

`AMDGIM_ERROR_CODE_FLAGS_TO_MAILBOX(c, f)` packs a 16-bit error code and 16-bit flags into one mailbox dword. `AMDGIM_ERROR_CODE(t, c)` packs a 4-bit category and 12-bit sub-error into a 16-bit code.

`enum AMDGIM_ERROR_VF` lists VF sub-errors such as ATOMBIOS init failure, missing VBIOS, GPU post error, clock query failure, fence init failure, driver init/IB/late-init failure, ASIC resume failure, GPU reset failure, and test. The comment requires the enum to stay in sync with the AMD GIM driver. `enum AMDGIM_ERROR_CATEGORY` defines GIM/PF/VF/VBIOS/monitor categories.

The exported functions are `amdgpu_vf_error_put()` and `amdgpu_vf_error_trans_all()`.

## Control Flow And Integration

Callers record VF errors with a category-specific sub-error, flags, and 64-bit data. Later, the transmit function drains pending records through the virtualization mailbox. The data buffer and lock are declared in `amdgpu_virt.h` as part of `struct amdgpu_vf_error_buffer`.

## State, Risks, And Tests

The header itself stores no state but defines an inter-component ABI. Risks include enum drift from GIM, incompatible packing assumptions, and insufficient category/code width for new errors. Test signals include compile-time checks for expected enum values where possible, mailbox packing tests, and integration tests that verify host-side decode of VF error reports.
