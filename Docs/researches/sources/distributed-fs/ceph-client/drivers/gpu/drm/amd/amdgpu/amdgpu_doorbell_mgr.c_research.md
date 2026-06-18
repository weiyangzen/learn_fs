# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell_mgr.c

## Purpose

`amdgpu_doorbell_mgr.c` implements the doorbell helper functions declared in `amdgpu_doorbell.h`. It bounds-checks 32-bit and 64-bit doorbell aperture accesses, translates doorbell BO-relative indices to BAR indices, initializes aperture metadata from PCI BAR2, allocates kernel doorbell storage, and frees it during teardown.

## Important APIs, types, and functions

- `amdgpu_mm_rdoorbell()` and `amdgpu_mm_wdoorbell()` read/write 32-bit doorbell dwords through `readl()` and `writel()`.
- `amdgpu_mm_rdoorbell64()` and `amdgpu_mm_wdoorbell64()` read/write 64-bit doorbells through `atomic64_read()` and `atomic64_set()`.
- `amdgpu_doorbell_index_on_bar()` computes `amdgpu_bo_gpu_offset(db_bo) / sizeof(u32) + doorbell_index * DIV_ROUND_UP(db_size, 4)`.
- `amdgpu_doorbell_create_kernel_doorbells()` allocates an `AMDGPU_GEM_DOMAIN_DOORBELL` kernel BO, maps CPU access into `adev->doorbell.cpu_addr`, reserves an extra page for MES ring-test use, and updates `num_kernel_doorbells` to the allocated dword count.
- `amdgpu_doorbell_init()` skips SI-era hardware, validates BAR2, calls `amdgpu_asic_init_doorbell_index()`, records BAR base/size, computes the kernel-reserved range from the maximum assignment, and adds a second page for Vega10+ paging queue assumptions.
- `amdgpu_doorbell_fini()` frees the kernel doorbell BO and CPU mapping.

## Control flow

Initialization first determines whether the ASIC supports doorbells. For supported ASICs it verifies PCI BAR2, initializes generation-specific assignments, records BAR base and length, and calculates how many dwords can be used by kernel assignments. If the range is nonzero, later kernel doorbell creation allocates a page-aligned doorbell-domain BO large enough for reserved assignments plus an extra MES page. Runtime ring code uses the read/write helpers to notify engines. Teardown frees the BO and CPU mapping.

## State and persistence behavior

The manager stores aperture state in `adev->doorbell.base`, `size`, `num_kernel_doorbells`, `kernel_doorbells`, and `cpu_addr`. `adev->mes.db_start_dw_offset` is set to the first dword of the extra MES page during kernel doorbell creation. Doorbell writes affect hardware engine notification state immediately and are not protected by software locks in this helper.

## Dependencies and integration points

This file depends on PCI resource BAR2, `amdgpu_asic_init_doorbell_index()`, AMDGPU BO kernel allocation/free helpers, `amdgpu_device_skip_hw_access()` for reset/suspend/no-HW-access paths, and consumers throughout ring/IP code that use doorbell writes for queue notification.

## Risks and edge cases

- Access helpers only check `index < num_kernel_doorbells`; wrong generation-specific index scaling can still target the wrong doorbell while staying in range.
- `amdgpu_device_skip_hw_access()` suppresses MMIO access during unsafe windows; callers must tolerate reads returning zero and writes being dropped.
- SI-era devices set all doorbell state to zero and return success, so consumers must not assume doorbells exist just because initialization succeeded.
- BAR2 unavailable or a zero computed assignment range returns `-EINVAL` and prevents doorbell use.
- The extra Vega10+ page changes `num_kernel_doorbells` after initial range computation, so bounds checks cover MES/paging queue use as well as static assignments.

## Test signals

Useful signals include successful `amdgpu_doorbell_init()` and kernel BO allocation, no "reading/writing beyond doorbell aperture" errors, passing ring tests that rely on WDOORBELL32/WDOORBELL64, MES ring test success using `db_start_dw_offset`, correct behavior when hardware access is skipped, and clean teardown without BO or mapping leaks.
