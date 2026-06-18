# sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Makefile

## Purpose
`virtual/Makefile` maps the virtual wireless Kconfig symbols to kernel build objects. It is the build glue for mac80211_hwsim and virt_wifi.

## Important Rules
- `obj-$(CONFIG_MAC80211_HWSIM) += mac80211_hwsim.o` builds the simulated mac80211 radio driver when enabled.
- `obj-$(CONFIG_VIRT_WIFI) += virt_wifi.o` builds the ethernet-to-wifi wrapper driver when enabled.

## Control Flow And Integration
The kernel build system expands each `obj-$()` rule based on the final configuration value. Built-in selections are linked into the kernel image; module selections produce `.ko` modules. The rules must match the symbols defined in `virtual/Kconfig` and the source filenames in the same directory.

## State And Persistence Behavior
There is no runtime state. Build outputs depend only on `.config` and source availability.

## Dependencies
Dependencies are declared in Kconfig rather than the Makefile. This file relies on normal kbuild semantics.

## Risks And Test Signals
Risks include symbol/file-name drift and missing object entries for new virtual drivers. Test with `CONFIG_MAC80211_HWSIM=y/m` and `CONFIG_VIRT_WIFI=y/m`, confirm object/module creation, and run clean builds to catch stale or renamed sources.
