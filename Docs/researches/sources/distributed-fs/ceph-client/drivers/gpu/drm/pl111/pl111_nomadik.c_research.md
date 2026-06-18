# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.c

Purpose: This Nomadik-specific helper switches the ST-Ericsson Nomadik PMU display mux into CLCD mode so the PL110-derived LCDC block, not the alternate MDIF block, drives the display path.

Important APIs, types, and functions: `pl111_nomadik_init(struct drm_device *dev)` looks up the PMU syscon via compatible string `stericsson,nomadik-pmu` and updates `PMU_CTRL_LCDNDIF` at `PMU_CTRL_OFFSET`. It is exported with `EXPORT_SYMBOL_GPL`.

Control flow: The function is intentionally opportunistic: if the PMU syscon is not present, it returns without error so multiplatform kernels can probe non-Nomadik PL111 devices. If the syscon exists, it clears the `LCDNDIF` bit through `regmap_update_bits()` and emits a DRM info message.

State and persistence: The only state change is persistent hardware register state in the PMU syscon, outside the DRM device itself. There is no local cache and no cleanup path to restore MDIF routing.

Dependencies and integration points: Depends on Linux MFD syscon/regmap APIs and is called from `pl111_amba_probe()` after Versatile variant detection and before IRQ/modeset initialization. It complements the Nomadik variant metadata in `pl111_drv.c`.

Risks: Silent return on syscon lookup failure is intentional but can hide device-tree binding mistakes. The mux write is unconditional once the PMU node exists, so systems sharing the PMU with another display pipeline rely on correct platform configuration.

Test signals: Boot a Nomadik/STn8815 device tree with PMU syscon present and verify the info log plus CLCD output; boot non-Nomadik PL111 systems and ensure this helper is a no-op; inspect PMU register values after probe.
