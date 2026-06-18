# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Makefile

## Purpose

This Makefile connects Visconti Kconfig symbols to object files. It builds the common Visconti pinctrl implementation and the TMPV7700 SoC data driver when their symbols are enabled.

## Important APIs, Types, And Data

- `obj-$(CONFIG_PINCTRL_VISCONTI) += pinctrl-common.o` builds the shared implementation.
- `obj-$(CONFIG_PINCTRL_TMPV7700) += pinctrl-tmpv7700.o` builds the TMPV7700 platform driver and descriptor tables.

## Control Flow

During kernel build, Kbuild evaluates these `obj-*` lines after Kconfig resolves symbols. `PINCTRL_TMPV7700` selects `PINCTRL_VISCONTI`, so enabling the concrete driver also includes the common object.

## State And Persistence

The file has no runtime state. It affects build artifacts by determining whether object files are linked into the kernel image.

## Dependencies And Integration Points

The Makefile integrates with the Visconti Kconfig file, Kbuild, and the platform driver implementation split between `pinctrl-common.c` and `pinctrl-tmpv7700.c`.

## Risks And Edge Cases

- If a future SoC selects `PINCTRL_VISCONTI` but omits its own object line, only the common code will build and no matching platform driver will bind.
- If `PINCTRL_TMPV7700` did not select `PINCTRL_VISCONTI`, this Makefile would allow the SoC object to build without the common implementation. Kconfig currently prevents that.

## Test Signals

The expected build signal is that `pinctrl-common.o` appears whenever `CONFIG_PINCTRL_VISCONTI=y`, and both objects appear when `CONFIG_PINCTRL_TMPV7700=y`.
