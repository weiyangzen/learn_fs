# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/module.c

Purpose: Module entry and exit wrapper for the Cypress/Infineon brcmfmac vendor plugin.

Important APIs/types/functions: `brcmf_cyw_init()` registers `BRCMF_FWVENDOR_CYW` with `brcmf_fwvid_register_vendor()`. `brcmf_cyw_exit()` unregisters it. Module metadata declares description, license, and `MODULE_IMPORT_NS("BRCMFMAC")`.

Control flow: Loading the module makes CYW vendor ops available. Unloading removes the vendor registration.

State and persistence behavior: Runtime state is in the fwvid registry only.

Dependencies and integration points: Uses core/bus/fwvid headers and local `vops.h`; depends on namespaced symbols from main brcmfmac.

Risks: Devices must not retain ops after vendor unregister; module ownership should enforce this. Registration collisions/failures propagate from init.

Test signals: Load/unload with main brcmfmac present; verify vendor registration, namespace imports, and failure unwind.
