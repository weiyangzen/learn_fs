# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-common.c

## Purpose
Provides the IPUv3 platform core: SoC matching, MMIO setup, clock/reset/memory initialization, IRQ-domain creation, IDMAC channel allocation/control, module clock gating, FSU/IDMAC linking, submodule initialization, and child platform-device registration for IPU clients.

## Important APIs, Types, and Functions
Major exported APIs include `ipu_get_num()`, color-space mapping helpers, `ipu_degrees_to_rot_mode()`, `ipu_idmac_get()/put()`, buffer readiness/select/clear helpers, IDMAC enable/disable/wait/watermark functions, `ipu_module_enable()/disable()`, CSI/IC source mux setters, `ipu_fsu_link()/unlink()`, `ipu_map_irq()`, `ipu_idmac_channel_irq()`, and `ipu_dump()`. `struct ipu_devtype` defines SoC offset maps and channel capabilities for i.MX51/i.MX53/i.MX6Q. `client_reg[]` describes child devices such as imx-ipuv3-crtc, csi, and other clients.

## Control Flow
`ipu_probe()` obtains OF match data, IRQs, memory resource, alias ID, optional PRG phandle for i.MX6QP DRM, maps common and IDMAC registers, gets/enables the bus clock, resets the device, resets internal memory, initializes the IRQ domain, programs display access timing, initializes submodules, then registers child platform devices. Removal unregisters children, exits submodules, removes IRQ mappings, and disables the bus clock. IDMAC users acquire channels through `ipu_idmac_get()`, configure CPMEM in other files, mark buffers ready, enable channels, and later disable and release them.

## State and Persistence
`struct ipu_soc` owns persistent runtime state for a probed IPU: device identity, devtype, MMIO bases, clock, IRQ domain, locks, channel list, submodule private pointers, and optional PRG private data. `channel_lock` protects IDMAC channel allocation; `ipu->lock` protects common register updates. Hardware state includes module enable bits, FSU links, IDMAC current/ready bits, IRQ masks/status, muxes, and reset state. There is no disk persistence.

## Dependencies and Integration Points
Uses platform/OF APIs, reset control via `device_reset()`, clk, generic IRQ chip/domain APIs, and submodule init/exit functions from CPMEM, CSI, IC, VDI, DP, DMFC, DI, DC, SMFC, and image-convert. It registers `ipu_pre_drv` and `ipu_prg_drv` before the main driver when DRM is enabled. Client devices use resources derived from the same IPU physical base and obtain exported GPL APIs to drive display/capture pipelines.

## Risks
Probe error unwinding is order-sensitive because clock, IRQ domain, submodules, and child devices have dependencies. IDMAC disable waits for busy status and manipulates double-buffer state; errors or races can leave channels active. FSU link tables only allow known source/sink pairs, and invalid links return `-EINVAL`. The IRQ cleanup comments indicate generic-chip removal is incomplete, so stale mappings are a maintenance risk. Channel allocation and module enable calls must be balanced by clients.

## Test Signals
Test probe/remove on supported compatibles, including reset failures and missing IRQ/resource cases. Exercise IDMAC allocation contention, double-buffer channel enable/disable, buffer-ready transitions, FSU link/unlink pairs, mapped EOF/NFACK IRQ delivery, and child-device creation. `ipu_dump()` register snapshots and dynamic debug around busy waits are strong diagnostics for stuck DMA or interrupt masking issues.
