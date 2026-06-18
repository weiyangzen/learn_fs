# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.c

## Purpose
`isp_v4_1_0.c` initializes and tears down ISP 4.1.0 support by presenting ISP capture, I2C, and GPIO/pinctrl blocks as MFD child devices with memory and IRQ resources derived from the amdgpu device.

## Important APIs, Types, And Functions
The exported function is `isp_v4_1_0_set_isp_funcs`, which installs `isp_v4_1_0_funcs`. Internal functions are `isp_v4_1_0_hw_init` and `isp_v4_1_0_hw_fini`. `isp_4_1_0_int_srcid` maps eight ISP ringbuffer write-pointer source IDs to Linux IRQ resources.

## Control Flow
Hardware init validates `adev->rmmio_size`, allocates three `mfd_cell` entries, a combined resource array for capture MMIO plus IRQs, platform data, a one-resource I2C MMIO array, and a one-resource GPIO MMIO array. It fills platform data with `adev`, ASIC type, and base RMMIO size; maps the main ISP register window, PHY0 window, eight IRQ mappings, the I2C0 window, and sensor GPIO window; then calls `mfd_add_hotplug_devices`. On allocation or MFD failure it frees allocated pieces and returns the error. Hardware fini removes child devices and frees all stored allocations.

## State And Persistence
State is stored in `struct amdgpu_isp`: `isp_cell`, `isp_res`, `isp_pdata`, `isp_i2c_res`, and `isp_gpio_res`. Child MFD devices persist after init until `mfd_remove_devices` in fini.

## Dependencies And Integration Points
Dependencies include `amdgpu.h`, `isp_v4_1_0.h`, `amdgpu_isp`, Linux MFD helpers, IRQ source mapping, DRM logging, and platform child drivers named `amd_isp_capture`, `amd_isp_i2c_designware`, and `amdisp-pinctrl`.

## Risks
The RMMIO size check compares against `0x5289`, which is smaller than the largest offsets used (`0x66700` plus size) if interpreted as absolute range, so resource validity depends on the meaning of `rmmio_size` and `rmmio_base`. Failure cleanup frees memory but does not null pointers, so repeated fini after failed init would be risky if callers do not respect return status. IRQ mapping failures are not checked for invalid mappings.

## Test Signals
Probe/remove tests, MFD child creation, resource ranges in sysfs, IRQ mapping delivery for all eight source IDs, I2C and GPIO child-driver binding, hotplug removal, and allocation-failure injection are useful signals.
