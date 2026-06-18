# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.h

Purpose: Declares ath10k spectral scan mode/config types and feature-gated spectral APIs.

Important APIs and types: Defines `struct ath10k_spec_scan` with `count` and `fft_size`, `enum ath10k_spectral_mode`, and declarations or stubs for `ath10k_spectral_process_fft()`, `ath10k_spectral_start()`, `ath10k_spectral_vif_stop()`, `ath10k_spectral_create()`, and `ath10k_spectral_destroy()`.

Control flow, state, and persistence: The header has no state. With `CONFIG_ATH10K_SPECTRAL` disabled, all functions become no-op success stubs, preserving call-site simplicity.

Dependencies and integration points: Includes shared spectral sample definitions from `../spectral_common.h` and references ath10k/WMI PHY error types.

Risks: Stub behavior means feature-disabled builds silently ignore spectral data and setup. Any API signature drift must remain synchronized with `spectral.c` and WMI PHY error callers.

Test signals: Build with spectral enabled and disabled; verify callers compile and that disabled builds return success without creating debugfs/relay state.
