# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.h

Purpose: Defines the private devlink state and constants for bnxt devlink integration. It provides helpers for mapping devlink objects back to `struct bnxt`, tracking remote reset preference, emitting remote reload notifications, and describing NVM-backed devlink parameters.

Important APIs, types, and functions: Defines `struct bnxt_dl`, `bnxt_get_bp_from_dl()`, `bnxt_dl_remote_reload()`, `bnxt_dl_get_remote_reset()`, `bnxt_dl_set_remote_reset()`, NVM offsets, MSI-X validation limits, `enum bnxt_nvm_dir_type`, `struct bnxt_dl_nvm_param`, `enum bnxt_dl_version_type`, and devlink public prototypes.

Control flow: Inline helpers are used by `bnxt_devlink.c` and firmware recovery code. `bnxt_dl_remote_reload()` reports that a remote reload performed driver reinit and firmware activate actions. Get/set helpers read and update `remote_reset` inside devlink private data.

State and persistence behavior: `struct bnxt_dl` stores the runtime back pointer and a runtime `remote_reset` boolean. NVM offsets describe persistent firmware variables but do not store them directly.

Dependencies and integration points: It depends on Linux devlink types and `struct bnxt` from `bnxt.h`. The NVM offsets and directory type constants are consumed by the devlink parameter get/set code, while health and register prototypes are called from probe/remove and firmware health paths.

Risks: `devlink_priv(dl)` must always contain `struct bnxt_dl`; using helpers with another devlink allocation would corrupt casts. NVM offsets are firmware ABI constants; mistakes can change unrelated persistent settings. The remote reload action mask should stay aligned with devlink reload actions exposed by `bnxt_devlink.c`.

Test signals: Compile devlink users, verify PF/VF devlink registration stores and retrieves `bp`, toggle remote reset and confirm state survives until recovery reprogramming, and validate each NVM offset against firmware documentation or device behavior.
