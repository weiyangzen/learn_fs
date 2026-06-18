<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.c

Purpose: Creates, initializes, suspends/resumes, and destroys the DCSS hardware device and its submodules.

Important APIs/types/functions: Public functions include `dcss_dev_create()`, `dcss_dev_destroy()`, `dcss_enable_dtg_and_ss()`, `dcss_disable_dtg_and_ss()`, and exported PM ops `dcss_dev_pm_ops`. Internal helpers manage clocks and submodule init/stop.

Control flow: Device creation fetches match data and MMIO resource, reserves memory, allocates `struct dcss_dev`, gets clocks, obtains port 0, initializes submodules with clocks enabled, sets autosuspend runtime PM, and returns the device. Submodule init orders BLKCTL, CTXLD, DTG, SS, DPR, and scaler. Runtime/system resume enables clocks, configures block control, resumes CTXLD, and resumes DRM modesetting; suspend does the reverse after mode-config suspend.

State and persistence behavior: `struct dcss_dev` stores device type offsets, base address, clock handles, submodule pointers, output mode, OF port, disable callback, and completion. Runtime PM controls clock persistence and volatile hardware state reinitialization.

Dependencies: Platform resources, OF graph, clocks, runtime PM, DRM mode config helpers, bridge connector header, and all DCSS submodule APIs.

Integration points: Top-level `dcss-drv.c` calls create/destroy. KMS/CRTC access `dcss` through `drm->dev_private`. PM ops are installed on the platform driver.

Risks: Error unwinding must stop only initialized submodules and release OF/clocks correctly. `devm_request_mem_region()` and manual submodule exits require careful lifetime assumptions. Resume order matters because context-loader writes depend on clocks and block control.

Test signals: Probe failure injection at each submodule, runtime autosuspend/resume, system suspend/resume, HDMI vs DSI output, module remove, and successful modeset after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.c -->
