# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.h

## Purpose
This header exposes the RTL8922A RFK helper surface used by the main chip implementation. It declares TSSI tracking control, RF channel setup, hardware RFK init, and channel pre/post RF hooks.

## Important APIs
- `rtw8922a_tssi_cont_en_phyidx(struct rtw89_dev *rtwdev, bool en, u8 phy_idx)`
- `rtw8922a_set_channel_rf(struct rtw89_dev *rtwdev, const struct rtw89_chan *chan, enum rtw89_phy_idx phy_idx)`
- `rtw8922a_rfk_hw_init(struct rtw89_dev *rtwdev)`
- `rtw8922a_pre_set_channel_rf(struct rtw89_dev *rtwdev, enum rtw89_phy_idx phy_idx)`
- `rtw8922a_post_set_channel_rf(struct rtw89_dev *rtwdev, enum rtw89_phy_idx phy_idx)`

## Control Flow and Integration
No code executes here. `rtw8922a.c` includes this header and assigns the functions into chip ops or calls them from channel helper sequences. The header decouples RFK-specific register programming from the larger chip implementation.

## State and Persistence
No state is owned in the header. Implementations mutate RF registers and `rtwdev` RFK/TSSI state.

## Dependencies
Depends on `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, and PHY index definitions.

## Risks
- Prototype drift from `rtw8922a_rfk.c` breaks build.
- The surface is small but timing-sensitive: callers assume pre/post hooks can be used around scheduler/BB reset channel transitions.

## Test Signals
- Compile coverage confirms prototypes match definitions.
- Runtime channel-switch and RFK tests exercise every declared function indirectly through `rtw8922a_chip_ops`.
