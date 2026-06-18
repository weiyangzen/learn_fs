# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.h

## Purpose
This header exposes RTL8922D RFK helper functions and the NCTL post RFK table to the main 8922D chip implementation.

## Important APIs
- `extern const struct rtw89_rfk_tbl rtw8922d_nctl_post_defs_tbl`
- `rtw8922d_tssi_cont_en_phyidx()`
- `rtw8922d_set_channel_rf()`
- `rtw8922d_rfk_hw_init()`
- `rtw8922d_rfk_mlo_ctrl()`
- `rtw8922d_pre_set_channel_rf()`
- `rtw8922d_post_set_channel_rf()`
- `rtw8922d_lck_track()`

## Control Flow and Integration
No code runs in the header. `rtw8922d.c` includes it to connect RFK helper implementations to chip ops and the chip info NCTL post table. The declarations form the boundary between general chip lifecycle code and RF-specific calibration code.

## State and Persistence
No state is owned here. Implementations mutate RF registers, RFK MCC data, TSSI state, and LCK thermal baselines.

## Dependencies
Depends on `core.h` for rtw89 device, channel, PHY index, and RFK table types.

## Risks
- Prototype mismatch breaks build.
- Callers rely on the declared pre/post channel hooks and LCK tracking semantics; changing signatures or behavior requires synchronized chip-op updates.

## Test Signals
- Compile/link coverage for `rtw8922d.c` and `rtw8922d_rfk.c`.
- Runtime RFK/channel/LCK tests exercise all declared functions indirectly.
