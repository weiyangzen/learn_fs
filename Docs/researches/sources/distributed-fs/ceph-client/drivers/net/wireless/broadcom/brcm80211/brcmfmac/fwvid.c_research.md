# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.c

Purpose: provides firmware-vendor dispatch for Broadcom/Cypress/BCA/WCC variants. It selects a vendor operation table for a driver instance, supports modular vendor implementations, tracks attached buses per vendor, and removes affected buses when a vendor module unregisters.

Important APIs/functions: `brcmf_fwvid_register_vendor` and `brcmf_fwvid_unregister_vendor` are exported when `brcmfmac` is modular. Core-facing functions are `brcmf_fwvid_attach`, `brcmf_fwvid_detach`, and `brcmf_fwvid_vendor_name`. The static vendor table stores vendor name, `brcmf_fwvid_ops`, attached driver list, optional module pointer, and registration completion.

Control flow and state: attach validates `bus_if->fwvid`, locks `fwvid_list_lock`, optionally requests `brcmfmac-<vendor>` and waits for registration, then installs `drvr->vops` and links the bus into the vendor list. Detach clears `drvr->vops` and removes the bus list node. Unregister walks attached buses, drops the lock around `brcmf_bus_remove`, then clears the module/ops and reinitializes completion.

Dependencies and integration: depends on `firmware.h` vendor IDs, vendor `vops.h` tables, bus removal, module auto-loading, completions, mutexes, and the inline wrappers in `fwvid.h`. It is the gate for vendor-specific feature attach, event allocation, cfg80211 operation selection, SAE password handling, and event registration.

Risks: `brcmf_fwvid_attach` returns early on module request failure without unlocking the mutex in the visible control path, which is a high-value audit target. Vendor unregister removes live buses, so list integrity and lock dropping/reacquisition must be correct. Built-in and module builds differ significantly; missing `alloc_fweh_info` is rejected only on registration.

Test signals: built-in vendor boot, modular vendor autoload, bad/unknown firmware vendor ID, vendor module unregister while devices are attached, repeated attach/detach, and lockdep around request-module failure paths.
