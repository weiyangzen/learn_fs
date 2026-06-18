# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.c

## Purpose
`ar9003_rtt.c` implements AR9003 radio retention table support for PCOEM builds. RTT stores selected radio calibration values per receive chain so they can be restored without rerunning the full calibration path. The file enables/disables RTT, reads and writes RTT table entries through the software table interface, captures table history into calibration data, clears it, and restores it during channel reset.

## Important APIs, Types, and Functions
The public functions are `ar9003_hw_rtt_enable()`, `ar9003_hw_rtt_disable()`, `ar9003_hw_rtt_set_mask()`, `ar9003_hw_rtt_force_restore()`, `ar9003_hw_rtt_load_hist()`, `ar9003_hw_rtt_fill_hist()`, `ar9003_hw_rtt_clear_hist()`, and `ar9003_hw_rtt_restore()`. Internal helpers are `ar9003_hw_rtt_load_hist_entry()`, `ar9003_hw_rtt_fill_hist_entry()`, and `ar9003_hw_patch_rtt()`.

The retained values live in `ah->caldata->rtt_table[AR9300_MAX_CHAINS][MAX_RTT_TABLE_ENTRY]`. The code also uses `ah->caldata->cal_flags`, especially `RTT_DONE` and `SW_PKDET_DONE`, and `ah->caldata->caldac[]` for peak-detector patching.

## Control Flow
`ar9003_hw_rtt_fill_hist()` iterates active RX chains, reads each of the six RTT entries through the software access register pair, patches entry 5 for chains 0/1 when software peak-detector calibration is present, logs the values, stores them in `caldata`, and sets `RTT_DONE`. `ar9003_hw_rtt_load_hist()` performs the reverse operation by writing stored values back into the hardware RTT table for active chains.

`ar9003_hw_rtt_restore()` is the main restore path. It first rejects missing `caldata`. If software peak-detector data exists, it writes chain 0/1 caldac overrides into 2 GHz or 5 GHz AGC fields and enables AGC override. It requires `RTT_DONE`, enables RTT, sets the restore mask to `0x30` with peak-detector data or `0x10` without it, requests the RF bus to stop baseband access, loads retained table entries, forces hardware restore, releases the RF bus, disables RTT, and returns whether restore completed.

## State and Persistence Behavior
RTT values persist in memory as part of per-channel calibration data. They are not written to disk or firmware. Hardware state is transient and explicitly enabled only around load/restore or calibration capture. `ar9003_hw_rtt_clear_hist()` writes zeros to all active-chain RTT entries and clears `RTT_DONE`, making future restore attempts fail until a new fill occurs.

## Dependencies and Integration Points
This file depends on `ar9003_phy.h` for RTT and 65 nm AGC register definitions and on `hw-ops.h` for RF bus operations exposed by PHY ops. `ar9003_calib.c` calls RTT restore before calibration, enables/clears RTT around calibration, fills history after successful calibration, and reloads history in some paths. The public declarations are gated by `CONFIG_ATH9K_PCOEM` in `ar9003_rtt.h`.

## Risks
The software table interface relies on short `udelay(1)` sequencing and `ath9k_hw_wait()` polling. `ar9003_hw_rtt_load_hist_entry()` silently returns on an access timeout, so a partial load can still be followed by forced restore. `ar9003_hw_rtt_fill_hist_entry()` returns `RTT_BAD_VALUE` on timeout and the caller stores it like a table value. Peak-detector patching only handles entry 5 and chains below 2, so hardware with more chains or different layout needs care. `ar9003_hw_rtt_restore()` calls `ath9k_hw_rfbus_done()` even on RF bus request failure, relying on the operation being harmless.

## Test Signals
Test signals include `RTT_DONE` being set after calibration, valid non-`RTT_BAD_VALUE` table entries, successful `ar9003_hw_rtt_force_restore()` waits, RF bus grant success, stable caldac override behavior on 2 GHz and 5 GHz, and no calibration regressions when `CONFIG_ATH9K_PCOEM` is disabled. Register traces should show RTT enable, mask write, table loads, force-restore bit self-clearing, and RTT disable in order.
