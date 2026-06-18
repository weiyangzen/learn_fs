# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.h

Purpose: Defines the per-VIF MLD state model, EMLSR state/reason enums, VIF access helpers, valid-link iteration helpers, and interface-level function prototypes.

Important APIs/types/functions: `enum iwl_mld_cca_40mhz_wa_status`, `enum iwl_mld_emlsr_blocked`, `enum iwl_mld_emlsr_exit`, `struct iwl_mld_emlsr`, `struct iwl_mld_vif`, `iwl_mld_vif_from_mac80211()`, `iwl_mld_vif_to_mac80211()`, `iwl_mld_vif_fw_id_valid()`, `iwl_mld_link_dereference_check()`, `for_each_mld_vif_valid_link`, and `iwl_mld_link_from_mac80211()`.

Control flow: The header does not implement large flows, but its helpers shape all VIF/link traversal. Valid link pointers are RCU-dereferenced with lockdep checks against `wiphy->mtx`, while `for_each_mld_vif_valid_link` provides the common active link iteration pattern used in cleanup and link management.

State/persistence: `struct iwl_mld_vif` separates restart-cleaned fields from persistent fields. Restart-cleaned fields include firmware ID, session protection, AP station, authorization, AP STA count, AP/IBSS activity, low-latency causes, and last link activation time. Persistent fields include the owning `mld`, default link object, RCU link pointers, EMLSR workers/state, WoWLAN/debugfs data, ROC activity, aux station, and MLO scan work.

Dependencies/integration: Includes mac80211, MLD link/session/D3/time-event definitions, and exports prototypes used by mac80211, firmware notification, low-latency, key, MLO, and scan code.

Risks: `iwl_mld_vif_fw_id_valid()` warns and fails if `fw_id` is out of the fixed MAC index array; many consumers rely on this guard before indexing per-MAC arrays. EMLSR blocked/exit reasons are bitmasks consumed across MLO code, so new reasons must not collide. RCU link pointers must be accessed only under the expected lock or RCU context.

Test signals: Build and lockdep coverage should verify helper use under `wiphy->mtx`. Unit tests around EMLSR transitions can assert that blocked and exit reason bits map cleanly into policy decisions.
