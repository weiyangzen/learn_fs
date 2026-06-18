<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile

## Purpose
The ADV748x Makefile defines how the composite `adv748x` driver object is built from its functional modules and gates it behind `CONFIG_VIDEO_ADV748X`.

## Important APIs, Types, and Functions
It declares `adv748x-objs` as `adv748x-afe.o`, `adv748x-core.o`, `adv748x-csi2.o`, and `adv748x-hdmi.o`, then adds `adv748x.o` to the build when the Kconfig symbol is enabled.

## Control Flow
There is no runtime control flow. Build order and object aggregation ensure all module-local symbols are linked into one driver.

## State and Persistence
No runtime state. The file controls build-system state only.

## Dependencies and Integration Points
It integrates with kbuild and the surrounding media I2C driver Kconfig. The object list mirrors the internal source split: core parent driver, analog front end, HDMI receiver, and CSI-2 transmitters.

## Risks
- Omitting any object breaks internal symbol resolution such as `adv748x_hdmi_init()` or `adv748x_tx_power()`.
- Adding a new ADV748x source file requires updating this list.

## Test Signals
Build `CONFIG_VIDEO_ADV748X=m` and `=y`, confirm the linked module exports one I2C driver, and verify no unresolved symbols from the split source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile -->
