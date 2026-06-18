# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Makefile

Purpose: Builds the Intel ipw2x00 legacy wireless drivers and shared libipw objects.

Important APIs/build targets: Builds `ipw2100.o` under `CONFIG_IPW2100`, `ipw2200.o` under `CONFIG_IPW2200`, and `libipw.o` under `CONFIG_LIBIPW`. `libipw-objs` consists of module, TX, RX, wireless extension, geo, spy, and WEP/TKIP/CCMP crypto implementation objects.

Control flow and state: Kbuild-only object composition. It determines which compilation units are linked into the shared libipw module.

Dependencies and integration: Mirrors symbols from `ipw2x00/Kconfig`. Integrates legacy driver objects with the deprecated IEEE 802.11 libipw stack and crypto helpers. Risks include object-list drift when libipw files change, config mismatches causing missing symbols, and GPL/SPDX consistency. Test signals include building each config independently, combined IPW2100/IPW2200 builds, LIBIPW-only dependency builds, and modpost symbol checks.
