# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.h

Purpose: defines the MLD PTP clock state and declares the small public PTP API used by MLD init/teardown and RX timestamp paths.

Important APIs/types: `struct ptp_data` contains the registered PHC pointer, `ptp_clock_info`, spinlock, delta and scaling anchors, scaled frequency, GP2 wrap tracking, and delayed work. Declarations expose init, remove, and adjusted-time conversion.

Control flow: MLD initialization calls `iwl_mld_ptp_init()` to register the PHC and set callbacks; teardown calls remove; timestamp consumers call `iwl_mld_ptp_get_adj_time()` while holding `ptp_data.lock`.

State and persistence: all PTP state is live kernel memory; `last_gp2` and `wrap_counter` are reset on removal. No persistent clock calibration is stored here.

Dependencies and integration: includes Linux `ptp_clock_kernel.h` and relies on `struct iwl_mld` from surrounding headers. The state is embedded in `struct iwl_mld`.

Risks and test signals: the contract requires callers of adjusted-time conversion to hold the spinlock, enforced by lockdep in implementation. Tests should check lock discipline and initialization failure behavior where `ptp_clock_register()` returns error or NULL.
