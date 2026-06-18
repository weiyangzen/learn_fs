<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.c

Purpose: Implements the i.MX8 DC display-engine component, including top-level display-engine register mapping, IRQ discovery, child population, and framegen/tcon initialization on runtime resume.

Important APIs/types/functions: Exports `dc_de_post_bind()` and platform driver `dc_de_driver`. Internal helper `dc_dec_init()` programs polarity control.

Control flow: Probe populates child devices and registers as a component. Bind allocates `struct dc_de`, maps top registers through regmap, fetches shdload/framecomplete/seqcomplete IRQs, enables runtime PM, identifies display index from MMIO base, and stores the pointer in `dc_drm->de[]`. Post-bind fills framegen and tcon pointers from the aggregate DRM device. Runtime resume initializes polarity, framegen, and tcon.

State and persistence behavior: Per-display `struct dc_de` holds regmap, device, framegen/tcon pointers, and IRQ numbers. Register state is volatile across power and reinitialized on runtime resume.

Dependencies: Component framework, OF platform population, runtime PM, regmap, clocks via child framegen, and shared `dc-drv.h`/`dc-de.h` contracts.

Integration points: CRTC instances use `dc_de` for IRQs and for access to framegen/tcon. The master driver calls `dc_de_post_bind()` after all components bind.

Risks: Base-address based id mapping assumes SoC address layout. `dc_de_post_bind()` assumes all required child components populated `dc_drm`; missing children can lead to null dereferences later.

Test signals: Component bind ordering, runtime resume after suspend, both display instances present, CRTC IRQ handling, and register writes for polarity/framegen/tcon init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.c -->
