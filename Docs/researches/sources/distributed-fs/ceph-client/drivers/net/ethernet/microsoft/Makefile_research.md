# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/Makefile

## Purpose
This Makefile connects the Microsoft Ethernet vendor directory to the MANA driver subdirectory.

## Important APIs, Types, and Data
- `obj-$(CONFIG_MICROSOFT_MANA) += mana/` descends into `microsoft/mana/` when the MANA option is enabled.

## Control Flow
Kbuild evaluates the single object-directory rule during kernel build. If `CONFIG_MICROSOFT_MANA` is unset, no Microsoft MANA objects are visited from this directory.

## State and Persistence
No runtime state. The file only affects build graph composition.

## Dependencies and Integration Points
- Consumes `CONFIG_MICROSOFT_MANA` from the adjacent Kconfig file.
- Integrates with the kernel's recursive Kbuild machinery.

## Risks and Edge Cases
- Any future Microsoft Ethernet driver would need its own rule here or a subdirectory-level Makefile addition.
- A mismatch between Kconfig symbol and Makefile symbol would silently omit the driver.

## Test Signals
- Building with `CONFIG_MICROSOFT_MANA=m` should produce the `mana` module from the child directory.
- Building with the option disabled should skip the directory.
