# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-pinctrl.h

## Purpose
This binding header provides pinctrl bit definitions and SoC-specific IOPAD helper macros for the TI K3 SoC family.

## APIs, Types, And Constants
The API defines bit shifts for wake, debounce, Schmitt trigger, pull, input, drive strength, isolation, and deep-sleep fields. User-facing macros include `PIN_OUTPUT`, `PIN_INPUT`, pull-up/down variants, no-Schmitt input variants, debounce levels, drive strength values, deep-sleep pin state helpers, wakeup helpers, and `PIN_GPIO_RANGE_IOPAD`. IOPAD helpers such as `AM62X_IOPAD`, `AM64X_IOPAD`, `AM65X_IOPAD`, `J721E_IOPAD`, and `J784S4_IOPAD` emit address offset plus config value cells.

## Control Flow And State
There is no runtime control flow. The macros build packed pin configuration values in DTS source; those values persist in DTBs and are consumed by K3 pinctrl drivers.

## Dependencies And Integration
The header has no includes and is included by TI K3 DTS files. It integrates with K3 pinctrl register layout and the `pinctrl-single`/TI pinctrl binding style.

## Risks And Test Signals
Risks include bit-shift errors, wrong pad-offset masking, and applying a SoC helper to the wrong pad domain. Tests include DTB compilation, `dtbs_check`, pinctrl probe logs, suspend/resume wake tests, and board-level validation of pull, input, and drive behavior.
