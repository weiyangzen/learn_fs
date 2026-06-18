<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ed.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ed.c

Purpose: Implements i.MX8 DC External Destination subdevices that select pixel-engine sources and trigger shadow synchronization into display outputs.

Important APIs/types/functions: Exports `dc_ed_pec_src_sel()`, `dc_ed_pec_sync_trigger()`, `dc_ed_init()`, and platform driver `dc_ed_driver`.

Control flow: Bind maps PEC and cfg register regions, initializes regmaps, gets the shdload IRQ, identifies the instance by MMIO base, and stores it as content or safety extdst. Init powers on PEC, enables shadow load, selects single sync mode, resets divider, sets external kick mode, disables perfcount/gamma, and initially selects no source.

State and persistence behavior: Holds device pointer, PEC/cfg regmaps, and shadow-load IRQ. Hardware source selection and sync-trigger registers are volatile and restored by pixel-engine runtime resume.

Dependencies: Component framework, platform resources/IRQs, regmap, and link IDs from `dc-pe.h`.

Integration points: CRTC enable/flush triggers extdst sync and waits for extdst shadow-load IRQs. Plane update switches content extdst between constframe and layerblend output.

Risks: Source selection silently returns on invalid source without warning, unlike layerblend. Missing shdload IRQ prevents CRTC completion waits. Instance mapping by hard-coded MMIO starts is SoC-specific.

Test signals: CRTC enable waiting for content/safety extdst shadow load, plane disable fallback to constframe, runtime resume init, and invalid link selection instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ed.c -->
