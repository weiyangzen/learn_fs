# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_drv.c

Purpose: platform-driver entry point for Komeda, tying hardware device creation to DRM/KMS registration and power management.

Important APIs/types/functions: `struct komeda_drv` stores `mdev` and `kms`. `dev_to_mdev()` exposes driver data to sysfs helpers. Probe/remove/shutdown manage lifecycle. Runtime and system PM hooks call Komeda suspend/resume and DRM mode-config suspend/resume. OF match table maps `arm,mali-d71`, `arm,mali-d32`, and `armchina,linlon-d6` to `d71_identify`.

Control flow: probe sets a 40-bit coherent DMA mask, allocates driver state, creates `komeda_dev`, enables runtime PM or resumes directly, attaches KMS, stores drvdata, and starts DRM clients. Remove detaches KMS, disables/suspends PM, destroys device, and clears drvdata. Shutdown performs atomic KMS shutdown.

State and persistence: per-platform `komeda_drv` persists in `dev_get_drvdata()`. Runtime PM state controls whether hardware is clocked/IRQ-enabled. DRM registration exposes device nodes and clients.

Dependencies/integration: Linux platform/OF/PM, DRM module platform driver macro, DRM client setup, `komeda_dev`, and `komeda_kms`.

Risks: drvdata is set after KMS attach, so sysfs/debugfs paths must not assume it during earlier create steps except where safe. Runtime PM disabled path manually resumes/suspends. Test signals: bind/unbind, module load/unload, system suspend/resume, runtime PM autosuspend behavior, DRM client/fbdev creation, and DMA mask failure injection.
