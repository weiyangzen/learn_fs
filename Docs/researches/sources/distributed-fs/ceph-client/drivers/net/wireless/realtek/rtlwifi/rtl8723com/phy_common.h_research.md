<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h

## Purpose
Declares shared RTL8723 PHY helper APIs and the channel-switch command structure used by chip-specific PHY code.

## Important APIs, Types, And Functions
- `RT_CANNOT_IO(hw)` currently expands to `false`.
- `enum swchnlcmd_id` defines channel-switch command opcodes: end, set TX power, BB write, port writes of several widths, and RF write.
- `struct swchnlcmd` stores command ID, two parameters, and millisecond delay.
- Prototypes cover BB register access, RF serial read/write, TX power index conversion, RF register definition initialization, channel-command setup, IQK matrix fill, ADDA/MAC save/restore, ADDA path enable, calibration MAC settings, path A standby, and PI mode switching.

## Control Flow
The header has no executable flow. Its enum and structure define the command language consumed by chip-specific channel-switch logic.

## State And Persistence
Declared functions operate on hardware BB/RF/MAC registers, `rtlphy->phyreg_def`, caller-provided backup arrays, and switch-command arrays. The header itself persists no state.

## Dependencies And Integration Points
Included by RTL8723AE/BE PHY code and common implementation. It is the shared ABI for PHY operations between chip modules and `rtl8723-common`.

## Risks And Edge Cases
Changing enum values or `struct swchnlcmd` layout can break channel-switch command tables. The `RT_CANNOT_IO` macro currently disables no IO; changing it affects all BB/RF access behavior. Prototype drift breaks exported common helper usage.

## Test Signals
Compile coverage for AE/BE PHY code, successful channel switching, RF register access, IQ calibration, and no ABI mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h -->
