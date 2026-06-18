# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_tkip.c

## Purpose
Implements host-based TKIP for libipw. It supplies the `TKIP` crypto plugin with RC4 key mixing, IV/ExtIV handling, WEP-style ICV encryption, Michael MIC generation/verification, replay protection, countermeasure flags, and Wireless Extensions MIC failure events.

## Important APIs, Types, and Functions
`struct libipw_tkip_data` stores the 32-byte TKIP key, key-set flag, TX/RX TSC fields, cached phase1 TTAK values, pending RX counters awaiting MIC verification, replay/ICV/MIC failure counters, key index, ARC4 contexts, and flags. Important functions include `libipw_tkip_init/deinit`, `tkip_mixing_phase1`, `tkip_mixing_phase2`, `libipw_tkip_hdr`, `libipw_tkip_encrypt`, `tkip_replay_check`, `libipw_tkip_decrypt`, `libipw_michael_mic_add`, `libipw_michael_mic_verify`, `libipw_michael_mic_failure`, key get/set, stats printing, and module init/exit.

## Control Flow
TX first honors TKIP countermeasures by dropping protected packets. It derives/caches phase1 TTAK by transmitter address and IV32, derives the per-packet RC4 seed with IV16, inserts an 8-byte TKIP header, appends a CRC32 ICV, encrypts payload plus ICV with ARC4, and advances TSC. MSDU-level encryption appends an 8-byte Michael MIC before fragmentation/MPDU encryption. RX validates countermeasures, length, ExtIV, key index, key presence, and replay state, decrypts the payload and ICV, stores new TSC in temporary fields, removes IV/ICV, and only commits RX counters after Michael MIC verification succeeds.

## State and Persistence Behavior
Per-key state preserves phase1 cache, TX/RX TSC, counters, and countermeasure flags. `set_key()` clears most state while preserving ARC4 context objects and key index, seeds TX IV16 to 1, and optionally seeds RX TSC from userspace. `get_key()` returns key material and current TX sequence. MIC failures increment local failure stats and send `IWEVMICHAELMICFAILURE` with pairwise/group classification derived from destination address.

## Dependencies and Integration Points
Depends on libipw crypto ops, kernel ARC4, CRC32, SKB mutation, `michael_mic()` from IEEE 802.11 helpers, Wireless Extensions events, and FIPS mode. `libipw_wx_set_encodeext()` loads it for `IW_ENCODE_ALG_TKIP`; `libipw_tx.c` invokes both MSDU and MPDU encryption hooks, while `libipw_rx.c` invokes MPDU decrypt before defragmentation and MSDU MIC verify after reassembly.

## Risks
TKIP is legacy and disabled under FIPS. Replay state is per key context, not per TID. RX counter commit is intentionally delayed until MIC verification; changing that order weakens replay/MIC behavior. In-place SKB edits require exact headroom and tailroom. Michael MIC failure events can trigger supplicant countermeasures, so false positives are user-visible. The phase1 cache must be invalidated correctly on IV32 changes and ICV failures.

## Test Signals
WPA/TKIP association, fragmented and unfragmented TX/RX, QoS data, replayed TSC rejection, bad ICV, bad Michael MIC and user event delivery, countermeasure flag drops, seeded RX sequence, key replacement, FIPS rejection, module unload, and mixed multicast/group key traffic are key signals.
