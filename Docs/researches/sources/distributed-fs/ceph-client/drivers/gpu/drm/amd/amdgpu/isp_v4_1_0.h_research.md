# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_0.h

## Purpose
`isp_v4_1_0.h` defines ISP 4.1.0 resource counts and MMIO offsets, imports ISP interrupt source IDs, and declares the function-table installer.

## Important APIs, Types, And Functions
Macros include `MAX_ISP410_MEM_RES`, `MAX_ISP410_SENSOR_RES`, `MAX_ISP410_INT_SRC`, `ISP410_PHY0_OFFSET/SIZE`, `ISP410_I2C0_OFFSET/SIZE`, and `ISP410_GPIO_SENSOR_OFFSET/SIZE`. The exported function declaration is `void isp_v4_1_0_set_isp_funcs(struct amdgpu_isp *isp);`.

## Control Flow
There is no control flow. The implementation consumes these constants when building MFD resources.

## State And Persistence
No state is owned here. Constants define persistent driver assumptions about ISP register layout and interrupt count.

## Dependencies And Integration Points
It includes `amdgpu_isp.h` and `ivsrcid/isp/irqsrcs_isp_4_1.h`. It integrates the ISP 4.1.0 implementation with amdgpu ISP setup and with platform child drivers that receive the resource windows.

## Risks
Incorrect offsets or sizes will expose wrong MMIO ranges to child devices. `MAX_ISP410_SENSOR_RES` is defined but not used in the companion implementation, so future sensor-resource changes need review. Header constants must stay synchronized with ASIC documentation.

## Test Signals
Build coverage, resource range inspection, child driver binding, and IRQ source validation are the main signals.
