# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath.h

Purpose: Shared Atheros wireless support header. It defines common device state, regulatory/key/cipher abstractions, register access operations, power-save hooks, cycle counters, debug masks, logging helpers, and common helper prototypes used by multiple Atheros drivers.

Important APIs/types/functions: `struct ath_common` is the core shared object with hardware/private pointers, mac80211 hardware, debug mask, op flags, ANI state, MAC/BSSID data, key cache bitmaps, crypto capabilities, cycle counters, regulatory data, operation tables, and supported bands. `struct ath_ops` abstracts register read/write, buffered writes, and read-modify-write operations. `struct ath_ps_ops` abstracts wake/restore hooks. Key APIs include `ath_key_config`, `ath_key_delete`, `ath_hw_keyreset`, `ath_hw_keysetmac`, `ath_rxbuf_alloc`, `ath_is_mybeacon`, `ath_hw_setbssidmask`, cycle counter helpers, and `ath_printk`.

Control flow: Individual drivers fill `ath_common` and operation tables, then call common helpers for key programming, regulatory setup, beacon recognition, and diagnostics. Debug macros compile to masked logging under `CONFIG_ATH_DEBUG` and to no-op stubs otherwise. Operation flags in `enum ath_op_flags` coordinate higher-level states such as beacons, ANI, scanning, reset, multi-channel, and WoW.

State/persistence: Maintains in-memory shared driver state only. Key cache bitmaps track hardware key slot allocation; regulatory fields mirror EEPROM/world regulatory decisions; cycle counters accumulate survey/ANI observations.

Dependencies/integration: Depends on mac80211, cfg80211 regulatory types, sk_buffs, spinlocks, Linux logging, and common Atheros implementation files built as `ath.o`.

Risks: `ATH_KEYMAX` fixes bitmap capacity; drivers with larger hardware key caches would need dynamic handling. Debug masks influence observability. Operation table callbacks must match bus/hardware locking expectations or common helpers can access registers unsafely.

Test signals: Cross-driver builds, key install/remove tests, regulatory domain selection, debugfs/module debug output, survey/cycle counter updates, and beacon detection behavior exercise the contracts in this header.
