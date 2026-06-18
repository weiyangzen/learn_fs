# sources/distributed-fs/ceph-client/drivers/nvdimm/security.c

Purpose: Implements the libnvdimm security sysfs command dispatcher and key-management glue for DIMM unlock, freeze, disable, update, erase, overwrite, and master-passphrase operations.

Important APIs and flow: Key helpers request encrypted keys named `nvdimm:<dimm_id>`, validate passphrase length, look up user-supplied key serials, and expose decrypted payloads under key semaphores. `__nvdimm_security_unlock()` handles pre-OS unlocked revalidation, normal unlock, security flag refresh, and incoherent-cache marking. `security_disable()`, `security_update()`, `security_erase()`, and `security_overwrite()` validate state, retrieve old/new keys, call provider security ops, refresh flags, and mark DIMMs incoherent after erase/overwrite. `nvdimm_security_overwrite_query()` polls asynchronous overwrite completion and notifies sysfs. `nvdimm_security_store()` parses textual commands and dispatches operations.

State and persistence behavior: Security state persists in DIMM hardware. Runtime flags include `nvdimm->sec.flags`, `ext_flags`, `overwrite_tmo`, `NDD_SECURITY_OVERWRITE`, `NDD_WORK_PENDING`, and `NDD_INCOHERENT`. Erase/overwrite/unlock can make CPU caches incoherent, causing region activation to invalidate caches before reuse.

Dependencies and integration points: Depends on keyrings, encrypted key payloads, provider `nvdimm_security_ops`, libnvdimm bus reconfiguration mutex, sysfs notifications, delayed work on `system_percpu_wq`, and region activation's incoherency handling.

Risks and test signals: Key serial logging assumes non-null keys even for zero-key paths, which needs careful provider behavior. Tests should cover missing provider ops, frozen state, overwrite busy polling and cancellation, active DIMM erase rejection, key length/type rejection, key revalidation disabled/enabled, master versus user passphrases, and sysfs command parsing limits.
