# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Makefile

## Purpose

This Makefile maps VT8500/WonderMedia pinctrl configuration symbols to Kbuild object files. It ensures the shared WMT pinctrl core and selected SoC descriptor drivers are compiled.

## Important APIs, Types, And Data

- `obj-$(CONFIG_PINCTRL_WMT) += pinctrl-wmt.o` builds the common core.
- SoC objects are selected by `CONFIG_PINCTRL_VT8500`, `CONFIG_PINCTRL_WM8505`, `CONFIG_PINCTRL_WM8650`, `CONFIG_PINCTRL_WM8750`, and `CONFIG_PINCTRL_WM8850`.

## Control Flow

After Kconfig selection, Kbuild includes object files whose config symbol is `y`. Each SoC option selects `PINCTRL_WMT`, so the shared implementation should be linked with any concrete SoC file.

## State And Persistence

There is no runtime state. The file controls build output and linking.

## Dependencies And Integration Points

It integrates with `vt8500/Kconfig`, the common `pinctrl-wmt.c` implementation, and SoC data files that call `wmt_pinctrl_probe()`.

## Risks And Edge Cases

- Adding a new SoC Kconfig option requires a matching Makefile object line and a selection of `PINCTRL_WMT`.
- Building multiple concrete SoC drivers into one kernel is supported by distinct object files, but they all rely on the shared common object.

## Test Signals

Build with each SoC config enabled and verify the common object and selected SoC object are present. Multi-SoC builds should link without duplicate symbol conflicts because each file uses static driver structures.
