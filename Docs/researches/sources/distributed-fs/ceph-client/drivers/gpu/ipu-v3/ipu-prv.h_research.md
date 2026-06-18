# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prv.h

## Purpose

`ipu-prv.h` is the private coordination header for the i.MX IPUv3 core driver. It centralizes common-register offsets, IDMAC register helpers, module enable bits, core-private state, and init/exit declarations for the IPU sub-blocks used by capture, display, image conversion, and prefetch/render helpers.

## Important APIs, Types, And Functions

Important definitions include `IPU_CM_*_REG_OFS`, `IPU_CONF`, flow-control register bit masks, IDMAC channel register macros, `IPU_NUM_IRQS`, `enum ipu_modules`, `struct ipuv3_channel`, and `struct ipu_soc`. Inline helpers `ipu_idmac_read()` and `ipu_idmac_write()` wrap IDMAC MMIO. The header declares module lifecycle functions such as `ipu_csi_init()`, `ipu_vdi_init()`, `ipu_smfc_init()`, `ipu_dp_init()`, `ipu_dc_init()`, `ipu_cpmem_init()`, `ipu_pre_*()`, and `ipu_prg_lookup_by_phandle()`.

## Control Flow

The header has no executable flow, but it defines the call graph used by IPU core probe and teardown: the core allocates `struct ipu_soc`, maps common and IDMAC registers, then initializes sub-block private objects that store back-pointers in `ipu_soc`. Consumer drivers later use exported public APIs to acquire channels or submodules whose private implementations rely on these declarations and register definitions.

## State And Persistence Behavior

Persistent state is represented by `struct ipu_soc`: device identity, type, common locks, channel list, common/IDMAC MMIO windows, IRQ domain, clock, use count, and pointers to submodule-private state. Hardware state persists in IPU common, flow, interrupt, buffer-ready/current-buffer, and IDMAC registers until changed by submodule code or reset.

## Dependencies And Integration Points

It depends on Linux device, clock, platform, MMIO, list, mutex/spinlock, and `video/imx-ipu-v3.h` public definitions. It integrates IPU internals with DRM, V4L2, capture, display, image conversion, PRE/PRG, and platform-driver submodules through shared private prototypes.

## Risks And Test Signals

Risks include register-offset drift across IPU revisions, shared bit definitions being used by multiple submodules with different locking expectations, unchecked macro arguments for channel register selection, and private struct changes breaking out-of-file users. Test signals are full IPUv3 build coverage, probe/remove on supported i.MX variants, IDMAC channel allocation, interrupt routing, and capture/display pipelines that exercise CSI, SMFC, VDI, IC, DP/DC/DI/DMFC, PRE, and PRG paths.
