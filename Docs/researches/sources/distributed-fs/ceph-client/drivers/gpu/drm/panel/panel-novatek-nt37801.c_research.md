# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37801.c

Purpose: DRM MIPI-DSI driver for Novatek NT37801/NT37810 AMOLED panels requiring Display Stream Compression. It exposes a 1440x3200 120 Hz mode and configures DSC unconditionally.

Important APIs, types, and functions: `struct novatek_nt37801` stores the DRM panel, DSI device, `drm_dsc_config`, reset GPIO, and regulator bulk pointer. Core functions are `novatek_nt37801_probe()`, `novatek_nt37801_prepare()`, `novatek_nt37801_unprepare()`, `novatek_nt37801_on()`, `novatek_nt37801_off()`, `novatek_nt37801_get_modes()`, and DCS backlight update.

Control flow: probe allocates panel state, obtains constant supplies `vddio`, `vci`, and `vdd`, gets reset GPIO, configures four-lane RGB888 DSI with no-EOT and non-continuous clock flags, marks `prepare_prev_first`, registers a raw 12-bit DCS backlight, adds the panel, fills `dsi->dsc` with DSC 1.1 parameters, and attaches. Prepare enables regulators, resets the panel, sends vendor command pages, packs and transmits a PPS, enables DSI compression mode, and waits. Unprepare sends display-off/sleep-mode, asserts reset, and disables regulators.

State and persistence: no durable state. The important runtime state is `ctx->dsc` and `dsi->dsc`, which must remain valid for the host while attached. Backlight writes temporarily leave low-power mode.

Dependencies and integration points: DRM panel, MIPI DSI, DRM DSC helper, regulator bulk const API, GPIO, backlight, and fixed-mode helper. Compatible string is `novatek,nt37801`.

Risks and test signals: DSC parameters are hard-coded and must match host capabilities and panel firmware. Compression enable happens after panel command init, so PPS and compression command failures must power down cleanly. The driver does not expose non-DSC fallback. Test with a DSI host that validates DSC, 1440x3200@120 mode timing, PPS transmission, compression enable, brightness update, regulator failure rollback, and suspend/resume.
