<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile

## Purpose
This Makefile maps Spreadtrum pinctrl Kconfig symbols to object files.

## Important Build Rules
- `obj-$(CONFIG_PINCTRL_SPRD) += pinctrl-sprd.o` builds the common Spreadtrum pinctrl core.
- `obj-$(CONFIG_PINCTRL_SPRD_SC9860) += pinctrl-sprd-sc9860.o` builds the SC9860 SoC-specific table/driver.

## Control Flow And Integration
The file participates in Kbuild only. Because `PINCTRL_SPRD_SC9860` selects `PINCTRL_SPRD`, a normal SC9860 build links both common and SoC-specific objects.

## State And Persistence
There is no runtime state. Build output depends entirely on `.config`.

## Dependencies
It depends on symbol names from the local `Kconfig` and source files named `pinctrl-sprd.c` and `pinctrl-sprd-sc9860.c` in the same directory.

## Risks And Review Notes
- Kconfig/Makefile symbol mismatch would silently omit required objects.
- Adding another SoC requires an additional object rule and a matching Kconfig symbol.
- If a SoC object is enabled without the common symbol selecting correctly, link failures or missing common APIs would result.

## Test Signals
Build with `CONFIG_PINCTRL_SPRD_SC9860=y` and `=m` to confirm both objects are included with the expected linkage. `make V=1 drivers/pinctrl/sprd/` should show `pinctrl-sprd.o` and `pinctrl-sprd-sc9860.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile -->
