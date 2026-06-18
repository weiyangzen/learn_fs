<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-drv.c

Purpose: Provides the top-level platform driver for the i.MX8MQ DCSS DRM device.

Important APIs/types/functions: Defines `struct dcss_drv`, `dcss_drv_dev_to_dcss()`, `dcss_drv_dev_to_drm()`, probe/remove/shutdown callbacks, SoC type-data table, OF match table, and `dcss_platform_driver`.

Control flow: Probe validates OF graph output, detects HDMI versus DSI remote endpoint, allocates driver state, creates the DCSS hardware device, stores drvdata, attaches KMS, and unwinds hardware on KMS failure. Remove detaches KMS and destroys DCSS. Shutdown asks KMS to shut down.

State and persistence behavior: `struct dcss_drv` stores pointers to `struct dcss_dev` and `struct dcss_kms_dev`. OF type-data encodes submodule offsets for i.MX8MQ.

Dependencies: DRM module platform driver helper, OF graph, platform driver APIs, `dcss-dev.h`, and `dcss-kms.h`.

Integration points: This is the module entry point selected by `CONFIG_DRM_IMX_DCSS`. It installs `dcss_dev_pm_ops` from `dcss-dev.c`.

Risks: Probe requires a remote graph endpoint; missing or deferred bridge endpoints cause `-ENODEV` rather than deferred probing. HDMI/DSI detection is based on one compatible string. KMS attach failure must shut down hardware cleanly.

Test signals: Probe with HDMI and DSI endpoints, missing endpoint behavior, KMS attach/remove, shutdown during active display, and runtime/system PM through platform driver ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-drv.c -->
