# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.h

Purpose: Declares the MLD MCC/regulatory API used by firmware startup and notification handling.

Important APIs/types/functions: `iwl_mld_init_mcc()`, `iwl_mld_handle_update_mcc()`, `iwl_mld_update_changed_regdomain()`, and `iwl_mld_get_regdomain()`.

Control flow: The header exposes initialization, async notification handling, on-demand changed-regdomain update, and direct regdomain fetch by alpha2/source.

State/persistence: State changes occur in `mcc.c`: wiphy regdomain, MCC source, and puncturing flags. The API contract notes that returned regdomains must be freed by the caller.

Dependencies/integration: Consumed by firmware startup and notification modules, and depends on cfg80211 regulatory types plus firmware MCC source enums from included MLD context.

Risks: Callers of `iwl_mld_get_regdomain()` own the returned pointer and must handle `ERR_PTR`/NULL. Most calls require `wiphy->mtx`, enforced in implementation.

Test signals: Build tests should catch type/signature drift; regulatory integration tests should confirm init and notification callers handle allocation and error returns correctly.
