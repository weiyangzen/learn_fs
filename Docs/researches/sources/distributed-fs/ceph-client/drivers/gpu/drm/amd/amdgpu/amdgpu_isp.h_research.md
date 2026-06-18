## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.h

Purpose: declares the ISP IP block interface and per-device ISP state used by `amdgpu_isp.c` and version-specific ISP implementations.

Important APIs/types: `ISP_REGS_OFFSET_END` bounds ISP register resources. `struct isp_funcs` provides `hw_init`, `hw_fini`, `hw_suspend`, and `hw_resume` callbacks. `struct amdgpu_isp` stores parent `struct device`, owning `amdgpu_device`, callback table, MFD cell and resources for ISP/I2C/GPIO, platform data, harvest config, firmware pointer, and a generic PM domain. It declares `isp_v4_1_0_ip_block` and `isp_v4_1_1_ip_block` as IP block versions.

Control flow contract: ASIC code installs one of the exported IP block versions; early init then fills `amdgpu_isp.funcs` with version-specific operations. The external ISP stack is expected to receive platform data and resources derived from this state.

State and persistence: all state is runtime in-memory. Firmware lifetime is associated with the device's firmware table and `adev->isp.fw`. MFD resources are references to kernel resource descriptors, not durable data.

Dependencies/integration: includes `drm/amd/isp.h` for external ISP platform data and Linux PM-domain support. It integrates AMDGPU DRM with an MFD/V4L2-style ISP child device.

Risks: callback pointers are optional at the type level but `amdgpu_isp.c` returns `-ENODEV` when missing; version-specific setup must populate them before lifecycle use. Resource pointers must remain valid for the lifetime of child devices.

Test signals: compile coverage for both ISP versions, platform-device creation, runtime suspend/resume, and buffer allocation from the external ISP driver.
