<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h

Purpose: Defines SolidRun vDPA driver shared data structures, logging helpers, config flags, MMIO helpers, and cross-file function prototypes.

Important APIs/types: `struct snet_vq` stores queue callback, state, ring addresses, size, serial ID, readiness, IRQ metadata, and kick pointer. `struct snet` embeds `vdpa_device` and owns config callback, control locks, VQs, negotiated features, status, DPU-ready state, config IRQ, BAR, PCI pointer, parent `psnet`, and device config. `struct snet_dev_cfg`, `struct snet_cfg`, and `struct psnet` model DPU-provided PF/VF configuration and parent state. Inline helpers read/write 32/64-bit values from PF/VF BARs.

Control flow: `snet_main.c` populates these structs from BAR config and vDPA ops. `snet_ctrl.c` consumes locks, offsets, and MMIO helpers for command protocol. `snet_hwmon.c` reads hwmon offsets through `psnet_read64()`.

State and persistence: All structs are runtime kernel state and MMIO views. Persistent behavior is DPU-owned and described by BAR config each probe.

Dependencies and integration points: Includes vDPA and PCI headers. Exposes optional hwmon prototype under `CONFIG_HWMON` and control prototypes used by main ops.

Risks: The packed struct declarations include pointers (`struct snet_dev_cfg **devs`, `void __iomem *virtio_cfg`) that are runtime-only and not directly firmware layout after parsing. IRQ and control locks must be initialized before use. `SNET_CFG_VER()` depends on PF negotiation in `psnet_read_cfg()`.

Test signals: Build all three SolidRun translation units together; runtime tests validate offsets, version checks, config flags, and MMIO read/write helpers under real or emulated BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h -->
