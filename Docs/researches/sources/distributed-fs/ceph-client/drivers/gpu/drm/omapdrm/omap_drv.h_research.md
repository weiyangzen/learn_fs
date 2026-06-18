# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.h

Purpose: Central private OMAP DRM header defining shared driver structures, logging macros, global atomic resource state, and cross-module prototypes.

Important APIs/types: `struct omap_drm_pipeline` groups a CRTC, encoder, connector, output, and display alias. `struct omap_global_state` embeds DRM private state and maps up to eight hardware overlays to DRM planes. `struct omap_drm_private` stores the DRM device, SoC revision, DSS/DISPC, pipeline/channel arrays, planes/overlays, global private object, workqueue, GEM list and lock, DMM/GART flags, zorder property, IRQ wait state, bandwidth limit, and fbdev pointer. Prototypes expose global atomic state accessors and debugfs init.

Control flow: `omap_drv.c` initializes this shared state; plane/overlay code uses global private state for resource assignment; CRTC/IRQ/GEM/fbdev/debugfs modules consume the private object and common includes.

State and persistence: Defines runtime state only. Lifetimes are tied to DRM device probe/remove and atomic transaction state.

Dependencies/integration: Includes DSS headers, DRM atomic/GEM/omap UAPI, and all major OMAP DRM private module headers. It is the include hub for the driver.

Risks and test signals: Fixed-size arrays of eight pipelines/channels/planes/overlays must cover supported hardware. Header inclusion can create broad rebuild impacts. Compile all OMAP DRM configurations and exercise multiple outputs/overlays to validate array indexing and global state duplication.
