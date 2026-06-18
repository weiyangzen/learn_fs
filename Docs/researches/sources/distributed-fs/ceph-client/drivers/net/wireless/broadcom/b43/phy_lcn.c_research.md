# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.c

## Purpose

`phy_lcn.c` implements the b43 LCN-PHY backend for Broadcom 802.11n LCN devices, primarily around radio 2064 and 2 GHz operation. It performs LCN allocation, baseband/radio init, channel setup, spur avoidance, AFE toggling, TX gain and initial TX power-control setup, temperature/voltage sense setup, IIR filter loading, RF kill, analog switching, and low-level PHY/radio access.

The exported `b43_phyops_lcn` operation table connects this code to the common PHY dispatcher. Like HT support, parts of LCN behavior are incomplete and marked with TODO/FIXME comments.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_lcn` provides allocation/free, prepare/init, PHY maskset, radio read/write, RF kill, analog switch, channel switch, default channel, and TX-power callbacks.
- `b43_phy_lcn_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_lcn` under `dev->phy.lcn`.
- `b43_phy_lcn_op_init()` initializes PHY registers, uploads LCN tables, runs rev0 baseband init and board-unit tweaks, initializes radio 2064, initializes TX power control for 2 GHz, switches to the current channel, and applies BCMA chip control writes.
- `b43_radio_2064_init()` and `b43_radio_2064_channel_setup()` program the radio 2064 registers used by LCN hardware.
- `b43_phy_lcn_set_channel()` and `_set_channel_tweaks()` perform channel-specific PLL/PMU/spur avoidance programming, radio tuning, AFE toggling, SFO configuration, CCK/OFDM transmit IIR filter selection, and table/register updates.
- `b43_phy_lcn_tx_pwr_ctl_init()`, `_set_tx_gain()`, `_set_tx_gain_override()`, `_set_bbmult()`, `_set_dac_gain()`, and `_clear_tx_power_offsets()` configure software-selected initial TX gain and power table state.
- `b43_phy_lcn_sense_setup()` temporarily saves many radio/PHY registers, suspends the MAC, configures auxiliary sense paths for temperature or VBAT, triggers a dummy transmission, restores registers, and resumes the MAC.
- `b43_phy_lcn_load_tx_iir_cck_filter()` and `_ofdm_filter()` select hardcoded filter coefficient sets by type and write them to PHY registers.
- `b43_phy_lcn_op_software_rfkill()` and `_switch_analog()` control radio/AFE power-down bits.

## Control Flow

After allocation and structure reset, initialization writes early PHY reset/AFE bits, initializes LCN tables, runs baseband and BU tweak sequences, initializes radio 2064 when the radio version matches, and starts TX power-control initialization in 2 GHz. It then calls the common channel switch for the current channel and programs BCMA chipcommon register-control/chip-control values.

Channel switching is operation-level limited to 2 GHz channels 1..14. The lower-level `b43_phy_lcn_set_channel()` first applies PLL/spur tweaks based on channel ranges, toggles the reset-like `0x44a` sequence, runs radio channel setup, delays, toggles AFE power, writes per-channel SFO constants, chooses a special channel-14 CCK IIR filter or normal channel filter type 25, writes an OFDM filter, and sets a final table-related PHY field.

TX power setup currently chooses fixed gain values and BB multiplier when hardware power control is not capable. If `hw_pwr_ctl_capable` is set, it logs that TX power control is not supported for this hardware. Recalc and adjust callbacks are stubs returning done/no-op, so the main dynamic behavior is the initial setup rather than a feedback loop.

RF kill expects a suspended MAC and logs if the MAC is enabled. Blocking writes multiple RF control override fields to power down portions of the radio path; unblocking clears those override bits rather than rerunning full radio init.

## State and Persistence

`struct b43_phy_lcn` is small and volatile. It stores:

- `hw_pwr_ctl`, whether hardware power control is enabled.
- `hw_pwr_ctl_capable`, whether hardware power control should be possible.
- `tx_pwr_curr_idx`, the current TX power index used by sense/setup paths.

Most LCN state lives directly in hardware registers or tables. `b43_phy_lcn_sense_setup()` has extensive local save/restore arrays for radio/PHY registers so temporary sense configuration does not persist. Channel and filter state persists in hardware after channel switching. `prepare_structs()` zeros the state each time the PHY is prepared.

## Dependencies and Integration Points

The file includes `b43.h`, `phy_lcn.h`, `tables_phy_lcn.h`, `main.h`, and Linux slab allocation. It depends on BCMA chipcommon/PMU helpers, mac80211 band/channel state, SPROM board flags and board revision, b43 PHY/radio/table helpers, MAC suspend/enable, dummy transmission, and common channel dispatch.

`b43_phy_lcn_tables_init()` and `b43_lcntab_write()` supply table initialization and table writes. `b43_phyops_lcn` is the integration point used by common b43 PHY selection for LCN devices.

## Risks and Edge Cases

- The file has many TODO/FIXME comments, including missing radio channel setup pieces, missing radio-init wait condition, hardcoded sense/table values, uncertain BU tweaks, and unimplemented TX power recalculation.
- Operation-level channel switching rejects 5 GHz; radio init has an explicit 5 GHz TODO.
- `b43_phy_lcn_tx_pwr_ctl_init()` logs unsupported hardware if `hw_pwr_ctl_capable` is true, which suggests the capable path is not implemented.
- `b43_phy_lcn_sense_setup()` saves register `0x4d0` twice in its save array, likely harmless but a maintenance smell.
- The CCK/OFDM IIR filter tables are hardcoded with comments noting brcmsmac was outdated and other values may need updating.
- RF kill and analog switching directly manipulate override bits and depend on caller suspension discipline.

## Test Signals

Validation should cover LCN allocation/init on radio 2064, successful LCN table upload, channel switches 1..14 with `-EINVAL` outside range, channel 14 selecting CCK filter type 3, normal channels selecting type 25 and OFDM type 0, no MAC enabled log during RF kill, and successful MAC suspend/resume around sense setup. Hardware logs should be checked for unsupported TX power-control messages and for correct PLL/spur behavior on channels 1..4/9..12 versus the other channels.
