# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/fsd-pinctrl.h

## Purpose
This binding header defines Tesla FSD pinctrl constants for pull, drive strength, and function selectors.

## APIs, Types, And Constants
It exports pull constants `FSD_PIN_PULL_NONE`, `FSD_PIN_PULL_DOWN`, and `FSD_PIN_PULL_UP`; drive levels `FSD_PIN_DRV_LV1`, `LV2`, `LV4`, and `LV6`; and function selectors for input, output, alternate functions 2 through 6, and external interrupt function `0xf`.

## Control Flow And State
There is no executable control flow. DTS files use these numeric constants in pin configuration properties, and the pinctrl driver interprets them at boot.

## Dependencies And Integration
The file has only include guards. It integrates with Tesla FSD DTS pinctrl nodes and the Samsung-derived/Tesla FSD pinctrl binding.

## Risks And Test Signals
Risks include wrong numeric encoding for drive strength or function mode, which can cause electrical or routing faults. Tests are DTB compilation, pinctrl driver probe, and board-level validation of configured GPIO/peripheral pins.
