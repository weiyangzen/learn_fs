<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig

## Purpose
This Kconfig file adds the pureLiFi vendor menu under Linux wireless drivers and conditionally includes the plfxlc driver Kconfig when `WLAN_VENDOR_PURELIFI` is enabled.

## Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_PURELIFI` as a boolean vendor selector defaulting to yes, with help text explaining that disabling it skips pureLiFi-specific questions. The `if WLAN_VENDOR_PURELIFI` block sources `drivers/net/wireless/purelifi/plfxlc/Kconfig`.

## Control Flow
During kernel configuration, selecting the vendor gate exposes the plfxlc device-support option. It does not by itself build code; it controls visibility of subordinate symbols.

## State And Persistence
The persistent output is the generated kernel `.config` choice for `WLAN_VENDOR_PURELIFI` and subordinate plfxlc symbols.

## Dependencies And Integration Points
Integrated by the parent wireless Kconfig tree. It delegates actual module selection and dependencies to `plfxlc/Kconfig`.

## Risks
If the source path changes or the vendor gate is disabled, the plfxlc option disappears from configuration menus. Default-y vendor gates increase menu visibility but do not force a module build.

## Test Signals
Run menuconfig/olddefconfig with the vendor symbol enabled and disabled and verify `CONFIG_PLFXLC` visibility and generated Makefile traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig -->
