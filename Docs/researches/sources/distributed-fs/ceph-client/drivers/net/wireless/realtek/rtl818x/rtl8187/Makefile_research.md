# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/Makefile

## Purpose
This Makefile builds the RTL8187 USB mac80211 driver from its device, RF, LED, and rfkill implementation files.

## Important APIs, Types, And Functions
`rtl8187-objs := dev.o rtl8225.o leds.o rfkill.o` defines the composite module object list. `obj-$(CONFIG_RTL8187) += rtl8187.o` connects the module to Kconfig. `ccflags-y += -I $(src)/..` exposes the parent `rtl818x.h` include directory.

## Control Flow
Build flow is controlled by Kbuild: when `CONFIG_RTL8187` is enabled, Kbuild links the listed objects into `rtl8187.o`.

## State And Persistence
No runtime state is defined. Build state is the object composition and include path.

## Dependencies And Integration Points
The object list matches source-level dependencies: `dev.c` owns USB/mac80211 registration, `rtl8225.c` owns RF/register helpers, `leds.c` owns optional LED class integration, and `rfkill.c` owns wiphy rfkill polling. The include flag allows local includes of `../rtl818x.h`.

## Risks
Because `leds.o` is always listed but its contents are guarded by `CONFIG_RTL8187_LEDS`, Kconfig/build coverage must ensure empty-object behavior remains acceptable. Removing the parent include path would break `rtl8187.h`'s `rtl818x.h` include.

## Test Signals
Signals are successful module build with `CONFIG_RTL8187=y/m`, successful build with LED support enabled and disabled, and link availability of `rtl8187_driver` plus helper symbols from all four objects.
