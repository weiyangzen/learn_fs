# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/spectral.h

Purpose: Declares the ath11k spectral scan state container and public spectral lifecycle/query API, with compile-time stubs when `CONFIG_ATH11K_SPECTRAL` is disabled.

Important APIs, types, and constants: `enum ath11k_spectral_mode` defines disabled, background, and manual modes. `struct ath11k_spectral` stores the direct-buffer RX ring, spinlock, relayfs channel, debugfs dentries, current mode, scan count, FFT size, enabled flag, and 160 MHz primary-fragment state. Exported declarations are `ath11k_spectral_init()`, `ath11k_spectral_deinit()`, `ath11k_spectral_vif_stop()`, `ath11k_spectral_reset_buffer()`, `ath11k_spectral_get_mode()`, and `ath11k_spectral_get_dbring()`.

Control flow: Consumers include this header and call init/deinit from ath11k device lifecycle, call `ath11k_spectral_vif_stop()` during vif teardown, call `ath11k_spectral_reset_buffer()` when relay contents should be discarded, and use `ath11k_spectral_get_dbring()` to route WMI direct-buffer releases. When spectral support is not built, all lifecycle functions become no-ops, mode reports disabled, and direct-buffer lookup returns `NULL`.

State and persistence behavior: The state is per `struct ath11k` radio and volatile. The comment marks `enabled` as protected by `lock`; in practice the implementation also uses `conf_mutex` around mode/config writes and `spectral.lock` around direct-buffer processing. Debugfs dentries and relayfs channel pointers are runtime registrations and must be cleared on unregister to avoid stale references.

Dependencies and integration points: The header includes the shared ath spectral sample definitions and ath11k direct-buffer ring definitions. It depends on `struct ath11k_base`, `struct ath11k`, and `struct ath11k_vif` definitions from core headers included by users. It provides the compile-time boundary between the main driver, WMI direct-buffer dispatch, debugfs spectral controls, and optional spectral build support.

Risks and edge cases: Stub behavior returning success can hide missing spectral support from callers unless they also check `ath11k_spectral_get_mode()` or debugfs presence. Locking expectations are split between `conf_mutex` and `spectral.lock`, so new fields added to `struct ath11k_spectral` need explicit ownership. `rfs_scan` and debugfs pointers are nullable and must be treated as optional after partial init failures.

Test signals: Build configurations should compile with `CONFIG_ATH11K_SPECTRAL=y/m` and disabled. Tests should confirm callers handle `NULL` direct-buffer rings and disabled mode when spectral support is absent, and that enabled builds initialize/clear every pointer in `struct ath11k_spectral` during normal and failure unwinds.
