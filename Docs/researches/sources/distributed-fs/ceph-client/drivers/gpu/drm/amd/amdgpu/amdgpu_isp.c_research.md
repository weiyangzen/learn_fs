## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.c

Purpose: integrates AMD ISP hardware as an AMDGPU IP block and exports buffer allocation helpers to an external V4L2/MFD ISP device. It selects version-specific ISP callbacks, loads ISP firmware for PSP, bridges runtime suspend/resume, and gives ISP clients GTT-backed GPU buffers.

Important APIs/functions: `isp_early_init()` selects `isp_v4_1_0_set_isp_funcs()` or `isp_v4_1_1_set_isp_funcs()` based on `amdgpu_ip_version()`, stores parent/device pointers, and calls `isp_load_fw_by_psp()`. `isp_hw_init()`, `isp_hw_fini()`, `isp_suspend()`, and `isp_resume()` delegate to `struct isp_funcs`. Exported symbols `isp_user_buffer_alloc/free()` import DMABUF-backed user buffers through `amdgpu_bo_create_isp_user()` and `amdgpu_bo_free_isp_user()`. Exported `isp_kernel_buffer_alloc/free()` allocate/free aligned GTT kernel BOs through AMDGPU BO helpers.

Control flow: early init decodes the firmware prefix, requests optional `amdgpu/<prefix>.bin`, registers it in `adev->firmware.ucode[AMDGPU_UCODE_ID_ISP]`, and increments PSP firmware size. Buffer allocation APIs convert the supplied device to a platform device, retrieve the first MFD cell's platform data, recover `adev`, validate that the ISP device parent is the AMDGPU device, then allocate and return BO handle plus GPU/CPU addresses.

State and persistence: runtime state is in `adev->isp`: callback table, firmware pointer, MFD resources, parent, harvest config, and generic PM domain. Buffer BOs are kernel objects whose lifetime is explicitly returned to the external ISP device via free calls; no disk persistence exists.

Dependencies/integration: depends on firmware loading, PSP firmware table, MFD platform data, Linux firmware APIs, BO/GART allocation helpers, and version-specific `isp_v4_1_0`/`isp_v4_1_1` implementations. It exports symbols for a V4L2 ISP driver outside the DRM device.

Risks: exported buffer APIs trust `mfd_cell[0].platform_data` after minimal checks; stale or malformed MFD data can crash before normal AMDGPU validation. `isp_kernel_buffer_alloc()` checks `!cpu_addr` instead of `!*cpu_addr`, so a null mapping would only be caught by `ret`. Firmware load failure makes early init fail with `-ENOENT`; optional firmware policy still releases on request failure.

Test signals: ISP-supported ASIC probe should select the correct callback table, load firmware, and complete IP lifecycle. External ISP tests should allocate/free user and kernel buffers, validate GPU address alignment (`ISP_MC_ADDR_ALIGN` for kernel buffers), and reject devices not parented by the AMDGPU device.
