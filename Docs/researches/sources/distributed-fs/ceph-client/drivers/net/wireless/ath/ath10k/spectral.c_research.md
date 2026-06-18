# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.c

Purpose: Implements optional ath10k spectral scan support, converting firmware PHY error FFT reports into relayfs sample records and providing debugfs controls for mode, sample count, and FFT bin count.

Important APIs and functions: Public functions are `ath10k_spectral_process_fft()`, `ath10k_spectral_start()`, `ath10k_spectral_vif_stop()`, `ath10k_spectral_create()`, and `ath10k_spectral_destroy()`. Internal helpers include `send_fft_sample()`, `get_max_exp()`, `ath10k_spectral_fix_bin_size()`, `ath10k_get_spectral_vdev()`, `ath10k_spectral_scan_trigger()`, and `ath10k_spectral_scan_config()`. Debugfs file operations back `spectral_scan_ctl`, `spectral_count`, and `spectral_bins`.

Control flow: WMI PHY error handling calls `ath10k_spectral_process_fft()`, which validates/fixes bin length, decodes FFT report registers, converts channel width to spectral sample conventions, fills an `fft_sample_ath10k`, interpolates the DC bin, and writes it to the relay channel. Debugfs writes under `conf_mutex` configure disabled/background/manual modes, trigger scans, or update count/bin settings. Creation opens a relay channel under the phy debugfs directory and creates control files; destroy closes the relay channel.

State and persistence: Mutates `ar->spectral.mode`, `ar->spectral.config.count`, `ar->spectral.config.fft_size`, `ar->spectral.rfs_chan_spec_scan`, and per-vif `spectral_enabled`. No durable persistence exists; settings reset in `ath10k_spectral_start()`.

Dependencies and integration points: Depends on `spectral_common.h`, ath10k debugfs state, WMI spectral enable/config commands, relayfs, and PHY error event parsing. It integrates with vif lifecycle through `ath10k_spectral_vif_stop()`.

Risks: FFT bin length, discard, and offset are hardware-parameter sensitive. The code rejects 80 MHz/64-bin samples due to known mismatch. Relay writes assume the generated TLV length fits the stack buffer. Debugfs commands require a valid vif and firmware WMI support; missing vifs return `-ENODEV`.

Test signals: Enable `CONFIG_ATH10K_SPECTRAL`, create/destroy debugfs files, switch disabled/background/manual modes, trigger scans, set invalid and valid bin counts, process 20/40/80 MHz FFT reports, verify DC interpolation and relay output, and stop a vif with active spectral scanning.
