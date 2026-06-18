<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile

## Purpose
This Makefile descends into the pureLiFi plfxlc driver directory when `CONFIG_PLFXLC` is enabled.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_PLFXLC) := plfxlc/`.

## Control Flow
Kbuild evaluates the config symbol and includes the `plfxlc/` subdirectory in the wireless driver build only when the driver is selected.

## State And Persistence
No runtime state exists. The persistent effect is build graph membership for the plfxlc module or built-in object tree.

## Dependencies And Integration Points
Depends on `CONFIG_PLFXLC` from `purelifi/plfxlc/Kconfig` and on Kbuild's directory traversal semantics.

## Risks
The rule is intentionally narrow; adding more pureLiFi drivers would require additional object entries. Misnaming `CONFIG_PLFXLC` or the directory would silently omit the driver.

## Test Signals
Build with `CONFIG_PLFXLC=m` and confirm `drivers/net/wireless/purelifi/plfxlc/plfxlc.ko` is produced; build with it disabled and confirm no descent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile -->
