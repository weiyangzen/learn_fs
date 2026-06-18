# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/module.c

Purpose: provides module lifecycle glue for the WCC brcmfmac firmware-vendor plugin.

Important APIs and functions: `brcmf_wcc_init()` registers `BRCMF_FWVENDOR_WCC`, `THIS_MODULE`, and `brcmf_wcc_ops` through `brcmf_fwvid_register_vendor()`. `brcmf_wcc_exit()` unregisters the same vendor. Module metadata describes the plugin, declares dual BSD/GPL licensing, imports namespace `BRCMFMAC`, and uses `module_init`/`module_exit`.

Control flow: when the module loads, the WCC vendor hooks become available to the main brcmfmac driver; unload removes them. The USB device table in `usb.c` sets many USB devices to `BRCMF_FWVENDOR_WCC`, so this registration is part of those devices' attach path.

State and persistence: module registration state lives in the brcmf fwvid registry. No per-device state is allocated here.

Dependencies and integration: depends on brcmf bus/core/fwvid APIs and the ops object from `core.c`. Integration failure prevents WCC-specific hooks from being resolved.

Risks and test signals: duplicate registration, unload while devices are active, or missing namespace exports can break module lifecycle. Test module load/unload, hotplug with WCC USB IDs, and unload refusal while referenced.
