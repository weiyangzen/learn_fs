# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.h

Purpose: Defines spectral scan modes, hardware FFT report layouts, per-device spectral scan state, max-magnitude/index helpers, and conditional spectral API declarations.

Important APIs/types: `enum spectral_mode` defines disabled, background, manual, and channel-scan modes. `struct ath_radar_info`, `ath_ht20_mag_info`, `ath_ht20_fft_packet`, `ath_ht20_40_mag_info`, and `ath_ht20_40_fft_packet` document PHY report tails and FFT metadata. `struct ath_spec_scan_priv` carries hardware pointer, relay channel, current mode, and hardware spectral config. Inline helpers decode max magnitude, signed max index, HT20/HT40 index mappings, and bitmap weight. Conditional declarations expose spectral init/deinit, trigger/config, and RX FFT processing.

Control flow: The implementation uses the structures for parsing but warns that full packet structs are reference-only because the MAC can vary sample byte counts. Callers initialize debug, configure mode, trigger scans, and feed spectral PHY error payloads through `ath_cmn_process_fft()`.

State/persistence: Persistent state is the `ath_spec_scan_priv` embedded in the driver softc. Constants define expected sample lengths and maximum stack buffer size.

Dependencies/integration: Includes `../spectral_common.h` for TLV and bin counts; depends on ath common/hardware types through included users.

Risks: Signed max-index decoding is subtle and bounds-clamps invalid values to zero. HT40 index remapping assumes lower/upper half layout. Feature-disabled builds turn most functions into no-ops; notably `ath9k_cmn_spectral_scan_config()` has no stub in this snapshot, so callers must be feature-gated.

Test signals: Compile with and without `CONFIG_ATH9K_COMMON_SPECTRAL`, max-index helper unit coverage for negative/positive bins, HT20/HT40 sample length constants, and real spectral TLV consumers.
