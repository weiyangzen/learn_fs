# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.c

## Purpose
This file implements RTL8225-SE radio tuning for the RTL8187SE/RTL8180-family PCI driver. It is a table-driven RF/baseband initializer plus the `rtl818x_rf_ops` implementation used by the main RTL8180 driver to detect, initialize, stop, and retune the radio.

## Important APIs, Types, And Functions
The exported entry point is `rtl8187se_detect_rf()`, which returns the static `rtl8225se_ops` object. That ops table provides `rtl8225se_rf_init()`, `rtl8225se_rf_stop()`, and `rtl8225se_rf_set_channel()`.

Low-level register access is handled by `rtl8187se_three_wire_io()`, `rtl8187se_rf_readreg()`, and `rtl8187se_rf_writereg()`, which program the RTL8187SE three-wire software interface through `SW_3W_*` registers and selected `rtl818x_csr` fields. Baseband writes go through inline helpers from `rtl8225se.h`, ultimately calling `rtl8180_write_phy()`.

The main static tuning helpers are `rtl8225se_write_zebra_agc()`, `rtl8187se_write_ofdm_config()`, `rtl8187se_write_rf_gain()`, `rtl8187se_write_initial_gain()`, and `rtl8225sez2_rf_set_tx_power()`. Hardware constants are held in RF gain, CCK/OFDM gain, channel, AGC, and OFDM configuration tables.

## Control Flow
Initialization first selects RF page 1 and reads registers 8 and 9 to infer whether the radio is D-cut. It then writes a long sequence of RF page 0/page 1 values, loads gain tables, performs sleeps required by the hardware, applies optional crystal calibration from `priv->xtal_cal`, writes power-save and baseband CCK/OFDM values, loads the Zebra AGC table, enables RF twice, enables the baseband, and ends by setting initial gain level 4.

Channel changes convert `conf->chandef.chan->center_freq` to an IEEE channel number, apply EEPROM-derived CCK/OFDM TX power from `priv->channels[channel - 1].hw_value`, write the PLL channel register, verify part of that register, retry if needed, and delay for settling.

Stop disables OFDM RXIQ matrix values, writes RF registers 4 and 0 to zero, waits, then powers down analog blocks via `rtl8180_set_anaparam()` and `rtl8180_set_anaparam2()`.

## State And Persistence
Persistent state is mostly external in `struct rtl8180_priv`: channel power values, crystal calibration values, and the memory-mapped register block. The file writes durable hardware state into RF registers, PHY registers, TX gain registers, antenna selection, and analog parameter registers, but does not maintain software state beyond stack temporaries.

## Dependencies And Integration Points
This file depends on `rtl8180.h` for `struct rtl8180_priv`, I/O helpers, analog-parameter helpers, and `rtl8180_write_phy()`. It depends on `rtl818x.h` register aliases such as `SW_3W_CMD1`, `SI_DATA_REG`, and `REG_ADDR*`. It is integrated into the larger RTL8180 PCI driver through `struct rtl818x_rf_ops`; the main device code calls the returned ops during start, stop, and channel configuration.

## Risks
The RF sequence is delay-sensitive and built from magic vendor values; reordering writes or reducing sleeps can leave the radio uncalibrated. `rtl8187se_three_wire_io()` casts byte buffers to integer pointers, so it assumes valid alignment and native endianness consistent with the existing driver environment. Channel indexes are based on 1-based 2.4 GHz channels and assume mac80211 will not request an unsupported channel. Failed three-wire busy waits are logged but not propagated, so later writes may proceed after hardware communication trouble.

## Test Signals
Useful signals are successful RF initialization messages showing D or non-D cut, association on all 2.4 GHz channels, TX power matching EEPROM-derived per-channel values, no three-wire busy warnings, stable receive sensitivity after AGC programming, and clean stop/start cycles without analog-power leakage. Channel-switch testing should verify the retry write on RF register 7 and absence of device stalls.
