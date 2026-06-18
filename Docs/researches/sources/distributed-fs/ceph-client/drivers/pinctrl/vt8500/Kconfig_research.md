# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/Kconfig

## Purpose

This Kconfig file defines pinctrl support options for VIA/WonderMedia VT8500-family SoCs. It has a hidden common support symbol and user-visible SoC-specific booleans for VT8500, WM8505, WM8650, WM8750, and WM8850.

## Important APIs, Types, And Data

- `PINCTRL_WMT` is a hidden common boolean selected by every concrete WMT-family driver. It selects `PINMUX` and `GENERIC_PINCONF`.
- `PINCTRL_VT8500` depends on `ARCH_WM8505` and supports VIA VT8500.
- `PINCTRL_WM8505` and `PINCTRL_WM8650` depend on `ARCH_WM8505`.
- `PINCTRL_WM8750` depends on `ARCH_WM8750`.
- `PINCTRL_WM8850` depends on `ARCH_WM8850`.
- The whole block is gated by `if ARCH_VT8500`.

## Control Flow

Configuration resolves under the `ARCH_VT8500` architecture family. Selecting any concrete SoC driver selects the common `PINCTRL_WMT` symbol. The Makefile then builds `pinctrl-wmt.o` and the selected SoC data object.

## State And Persistence

The file has no runtime state. Its persistence is the generated kernel config and resulting linked objects.

## Dependencies And Integration Points

It integrates with architecture Kconfig symbols, the generic pinmux and pinconf subsystems, and the vt8500 Makefile. Concrete drivers are `bool`, so enabled support is built in.

## Risks And Edge Cases

- `PINCTRL_VT8500` depending on `ARCH_WM8505` looks historically tied to the architecture family naming; changing architecture symbols could accidentally hide VT8500 support.
- Because all options are inside `if ARCH_VT8500`, `COMPILE_TEST` does not appear to expose these drivers on unrelated architectures.
- The common symbol must stay selected by every concrete driver or the SoC object will lack its shared implementation.

## Test Signals

Kconfig tests should verify visibility under each architecture symbol and that selecting a SoC driver selects `PINCTRL_WMT`. Build logs should show `pinctrl-wmt.o` plus the chosen SoC object.
