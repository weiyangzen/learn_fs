# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.c

Purpose: implements the Arm Ethos-U platform DRM accel driver: device-tree probe/remove, reset and runtime PM, SRAM setup, NPU info discovery, DRM ioctls, open/close, and DRM driver registration.

Important APIs/functions: ioctl handlers query NPU info, create/wait/mmap BOs, create validated command-stream BOs, and submit jobs. `ethosu_reset()` resets the NPU to non-secure mode, configures region and AXI/memory attributes for U65/U85, and clears SRAM. Runtime PM callbacks enable/disable clocks and reset on resume. `ethosu_init()` resumes hardware, enables autosuspend, reads ID/config, initializes SRAM, and logs capabilities. `ethosu_probe()` allocates DRM device, sets DMA mask, maps registers, gets clocks, initializes jobs, initializes hardware, registers DRM, and autosuspends.

Control flow: users open the accel node, receive per-file scheduler entity state, allocate BOs/command streams, and submit jobs. Remove unregisters DRM, finalizes scheduler, and frees SRAM allocation.

State and persistence: `ethosu_device` stores clocks, regs, SRAM pool/allocation, NPU info, scheduler/fence/job state. Runtime PM core tracks active/suspended state.

Dependencies: platform device/OF, DRM accel/GEM/ioctl, PM runtime, clocks, genalloc SRAM, Ethos-U GEM/job helpers, UAPI.

Risks: `devm_platform_ioremap_resource()` result is assigned without explicit `IS_ERR()` check here. Runtime PM init ordering must balance refs. Reset configuration differs by generation and can break memory routing.

Test signals: probe for U65/U85 compatibles, missing clocks/IRQ/SRAM, all ioctls with invalid pads/sizes, suspend/resume, NPU query ABI, and remove with open files/jobs.
