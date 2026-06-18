# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.c

Purpose: Implements spectral scan FFT sample parsing, validation, relayfs output, debugfs controls, and hardware trigger/configuration helpers.

Important APIs/functions: Exported APIs are `ath_cmn_process_fft()`, `ath9k_cmn_spectral_scan_trigger()`, `ath9k_cmn_spectral_scan_config()`, `ath9k_cmn_spectral_init_debug()`, and `ath9k_cmn_spectral_deinit_debug()`. Internal handlers validate HT20 and HT20/40 max-index/magnitude metadata, construct `fft_sample_ht20` or `fft_sample_ht20_40` TLVs, compensate for missing/extra MAC bytes, and write samples to a relay channel.

Control flow: RX processing accepts only radar/false-radar/spectral PHY errors with the spectral bit set. If relay buffers are full, it reports the frame as consumed without parsing. It chooses HT20 or HT40 parsing from the current chandef, scans the raw report for FFT sample boundaries, validates metadata, fixes the single-sample short/extra-byte cases when possible, emits TLVs, increments good/error spectral sample counters, and mixes bin data into the kernel randomness pool. Debugfs `spectral_scan_ctl` reads/writes mode strings (`disable`, `background`, `chanscan`, `manual`, `trigger`). Trigger enables PHYRADAR/PHYERR RX filters, reconfigures hardware, and calls the hardware spectral trigger op.

State/persistence: State lives in `struct ath_spec_scan_priv`: `ah`, relay channel pointer, current `spectral_mode`, and `spec_config` fields (`enabled`, `endless`, `short_repeat`, `count`, `period`, `fft_period`). Persistent debugfs files control config; relayfs buffers persist until deinit.

Dependencies/integration: Uses `linux/relay.h`, `linux/random.h`, spectral common TLV definitions, ath hardware ops (`spectral_scan_trigger`, `spectral_scan_config`), power-save ops, RX stats macros, debugfs, and channel scan triggering from `channel.c`.

Risks: FFT reports can be malformed by hardware byte insertion/deletion; parser recovery is intentionally conservative. Buffer-full conditions drop processing. Spectral and DFS both use PHY error paths and cannot be used concurrently during DFS radar detection. TX99 disables spectral control. User debugfs writes directly affect hardware scan mode and RX filter.

Test signals: HT20 and HT40 FFT reports, single-sample correction cases, malformed/truncated reports, relay buffer full handling, debugfs mode/config writes, channel-scan trigger on channel change, spectral disabled under TX99, and RX stats for good/error samples.
