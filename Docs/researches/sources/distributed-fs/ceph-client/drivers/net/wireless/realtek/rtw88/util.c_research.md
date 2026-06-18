## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.c

Purpose: small shared utility layer for rtw88 hardware polling, LTE coexistence register access, register restoration, descriptor-rate conversion, and safe non-atomic iteration over stations/VIFs.

Important APIs/functions: `check_hw_ready()` polls a masked register for up to 1000 iterations with 10 us delay. `ltecoex_read_reg()` and `ltecoex_reg_write()` use chip LTE coexistence control/data registers after readiness polling. `rtw_restore_reg()` restores a table of 1/2/4-byte backup registers. `rtw_desc_to_mcsrate()` maps descriptor rate IDs into mac80211 MCS/NSS. `rtw_iterate_stas()` and `rtw_iterate_vifs()` collect atomic mac80211 iteration results into temporary lists, then call a non-atomic callback while `rtwdev->mutex` is held.

Control flow: polling helpers are synchronous. Iteration helpers allocate list entries with `GFP_ATOMIC` in the mac80211 atomic iterator, then process and free them outside the iterator, relying on the caller-held mutex to prevent removal.

State and persistence: no persistent state beyond temporary lists. Register helpers mutate hardware, and rate conversion mutates caller-provided output pointers.

Dependencies and integration: used by WoWLAN pattern CAM polling, LTE coexistence code, IQK/register restore paths, RX status filling, and firmware media/key iteration helpers.

Risks and test signals: risks include silent iteration entry allocation failure, required mutex not held, unsupported backup lengths ignored, and timeout-sensitive polling. Test with lockdep, hardware timeout injection, LTE coexistence paths, and RX rate mapping for HT/VHT rates.
