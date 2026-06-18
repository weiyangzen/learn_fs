# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.c

Purpose: Provides shared module initialization, module parameter plumbing, platform/OF/DMI/ACPI settings aggregation, firmware preinit commands, blob download helpers, and logging implementations.

Important APIs/types/functions: Module params include `txglomsz`, `debug`, `p2pon`, `feature_disable`, `alternative_fw_path`, `fcmode`, `roamoff`, `iapp`, and debug-only `ignore_probe_fail`. Public functions include `brcmf_c_set_joinpref_default()`, `brcmf_c_preinit_dcmds()`, `brcmf_c_set_cur_etheraddr()`, `brcmf_get_module_param()`, `brcmf_release_module_param()`, `__brcmf_err()`, and `__brcmf_dbg()`.

Control flow: Module init probes optional platform data, initializes global firmware path, then registers SDIO/USB/PCIe bus support through `brcmf_core_init()`. Per-device settings come from module params, platform data, DMI, OF, and ACPI. `brcmf_c_preinit_dcmds()` programs or reads MAC address, handles default-template MAC replacement, reads revinfo, loads CLM/TxCap/calibration blobs, queries firmware/CLM versions, enables `mpc`, join preference, IF events, scan timing, and best-effort TX beamforming.

State and persistence behavior: Global state includes module params, `brcmf_msg_level`, platform data, and alternate firmware path. Per-device settings and firmware version/revinfo live in runtime driver objects.

Dependencies and integration points: Uses fwil, bus blob access, firmware settings, chip name formatting, platform data, OF, DMI, ACPI, and core bus registration.

Risks: Preinit is a long fatal chain except missing CLM/TxCap blobs. Random MAC replacement changes identity. Module params can globally alter probe behavior.

Test signals: Module load/unload, absent/present CLM/TxCap/calibration, platform data power hooks, OF defer, firmware version logs, and IF event mask programming.
