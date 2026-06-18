<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fw.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fw.c

Purpose: Implements the FetchWarp fetchunit instance for the i.MX8 DC pixel engine.

Important APIs/types/functions: Defines `struct dc_fw`, `dc_fw_set_fmt()`, `dc_fw_set_framedimensions()`, `dc_fw_init()`, operation installation, and platform driver `dc_fw_driver`.

Control flow: Bind maps PEC and cfg register regions, creates regmaps, identifies instance id 2, fills per-fraction register offsets, assigns link id `LINK_ID_FETCHWARP2`, installs common fetchunit ops with FetchWarp-specific format/framedimension/init overrides, and stores it in `dc_drm->fu_disp[]`.

State and persistence behavior: Maintains a `dc_fu` with PEC/cfg regmaps and volatile register state. Init selects no PEC source and applies common fetchunit initialization.

Dependencies: Component/platform/regmap frameworks, DRM fourcc, common fetchunit helpers, and DC pixel-engine link IDs.

Integration points: Available to the pixel-engine display fetchunit array and layerblend secondary selection. The current primary-plane path can select fetchunits by plane index.

Risks: FetchWarp format setup writes both control and layer-property fields and assumes supported formats from higher-level checks. Address-based id mapping is SoC-specific.

Test signals: Probe of the fetchwarp node, runtime PM reinit, plane update using the second fetchunit path, and register traces for format/control programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fw.c -->
