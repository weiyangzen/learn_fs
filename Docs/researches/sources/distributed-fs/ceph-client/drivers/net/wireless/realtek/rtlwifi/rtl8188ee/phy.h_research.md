# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.h

## Purpose

`phy.h` defines RTL8188EE PHY-layer constants, EEPROM offsets, channel-switch command structures, configuration enums, antenna and antenna-diversity enums, EFUSE/TX-power helper structures, and the public PHY function prototypes implemented in `phy.c`.

## Important APIs, Types, And Constants

`struct swchnlcmd` and `enum swchnlcmd_id` define the staged channel-switch command format. `enum baseband_config_type` selects PHY register versus AGC table loading. `struct efuse_contents`, `struct tx_power_struct`, and related offset macros describe EFUSE and TX-power data shapes. `enum _ANT_DIV_TYPE` defines the antenna-diversity modes consumed by both `phy.c` and `dm.c`.

The exported prototypes cover BB/RF register access, MAC/BB/RF configuration, original hardware register snapshotting, TX-power get/set, scan backup/restore, bandwidth changes, channel switching, IQK/LCK calibration, RF path switching, RF header-table config, PHY IO commands, and RF power-state changes.

## Control Flow And Integration

This header is included by `hw.c`, `dm.c`, and RF-related RTL8188EE modules. It does not execute logic, but its structures drive `phy.c` command staging and EFUSE interpretation. Constants such as `MAX_TX_COUNT`, IQK register counts, and EEPROM offsets must remain synchronized with table parsing and EFUSE layouts.

## State And Persistence Behavior

No state is allocated here. The declared structures describe state stored in `rtlphy`, `rtlefuse`, or stack temporaries in implementation files. The enums and macro values directly affect persisted hardware register programming and calibration behavior.

## Dependencies, Risks, And Test Signals

The header depends on shared rtlwifi channel, RF path, IO type, and power-state enums. Risks include duplicated macro definitions (`IQK_ADDA_REG_NUM`, `IQK_MAC_REG_NUM`) and magic EEPROM offsets becoming inconsistent with hardware documentation. Build tests, table parser tests, EFUSE decode tests, and end-to-end PHY init/channel/power tests are the relevant signals.
