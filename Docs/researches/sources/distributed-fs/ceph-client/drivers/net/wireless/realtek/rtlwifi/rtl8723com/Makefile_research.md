<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile

## Purpose
Builds the shared RTL8723 common rtlwifi object used by both RTL8723AE and RTL8723BE drivers.

## Important APIs, Types, And Functions
- `rtl8723-common-objs` lists `main.o`, `dm_common.o`, `fw_common.o`, and `phy_common.o`.
- `obj-$(CONFIG_RTL8723_COMMON) += rtl8723-common.o` hooks the composite object into Kbuild when the common config symbol is enabled.

## Control Flow
Kbuild compiles the listed objects and links them into `rtl8723-common.o` when `CONFIG_RTL8723_COMMON` is set. There is no runtime control flow.

## State And Persistence
The file affects build artifacts only: object files and the resulting kernel module or built-in object. It stores no runtime state.

## Dependencies And Integration Points
Integrated by the Linux kernel Kbuild system under the rtlwifi driver tree. Chip drivers select or depend on `CONFIG_RTL8723_COMMON` so shared DM, firmware, PHY, and module metadata code is available.

## Risks And Edge Cases
Removing an object from `rtl8723-common-objs` can create unresolved symbols in RTL8723AE/BE modules. Incorrect config gating can build chip drivers without shared helpers.

## Test Signals
Signals include `CONFIG_RTL8723_COMMON=m/y` builds, successful linking of RTL8723AE/BE, and no unresolved exported symbol errors for common helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile -->
