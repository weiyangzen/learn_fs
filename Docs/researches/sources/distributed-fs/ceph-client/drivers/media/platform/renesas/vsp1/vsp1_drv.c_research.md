# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drv.c

Purpose: platform driver core for Renesas VSP1/VSP2. It probes resources, identifies hardware variants, creates entities and media links, handles IRQs and runtime PM, and registers either a V4L2 userspace media graph or an internal DRM/VSPX pipeline.

Important APIs and functions: `vsp1_irq_handler()`, `vsp1_create_entities()`, `vsp1_destroy_entities()`, `vsp1_device_init()`, `vsp1_reset_wpf()`, `vsp1_device_get()`, `vsp1_device_put()`, PM callbacks, `vsp1_lookup_info()`, `vsp1_probe()`, and `vsp1_remove()`. The large `vsp1_device_infos[]` table maps IP versions to features and entity counts.

Control flow: probe allocates `vsp1_device`, maps MMIO, gets IRQ/reset/FCP, enables runtime PM, reads or synthesizes the version, masks stale interrupts, requests IRQ, and creates entities. Entity creation instantiates feature-gated processors, RPF/WPF/video nodes, registers subdevs, then either creates userspace media links and subdev nodes or initializes DRM/VSPX support. IRQ handling scans WPFs, acknowledges DFE/FRE/UND bits, counts underruns, and dispatches frame-end handling.

State and persistence: persistent state is rooted in `struct vsp1_device`, entity/video lists, hardware feature table, runtime PM state, reset/FCP resources, media/V4L2 devices, and optional DRM/VSPX private state. Runtime resume resets routes to unused, resets active WPFs, configures display-list engine, and enables FCP.

Dependencies and integration: depends on platform device, OF match data, reset controller, runtime PM, R-Car FCP, V4L2/media core, and every VSP1 entity constructor.

Risks and test signals: risks include incomplete cleanup after partial entity creation, unsupported version detection, interrupt acknowledgment polarity, runtime PM reset side effects, and feature-count mismatches. Test probe/remove deferral, suspend/resume, all compatible strings, UAPI media graph enumeration, DRM display operation, and WPF underrun logging.
