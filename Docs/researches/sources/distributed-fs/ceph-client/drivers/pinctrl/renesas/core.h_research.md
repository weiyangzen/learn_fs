# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/core.h

## Purpose
`core.h` is the internal interface for the Renesas/SuperH PFC core. It shares the small set of common data structures and functions needed by `core.c`, `pinctrl.c`, and `gpio.c`.

## Important APIs And Types
- `struct sh_pfc_pin_range { u16 start; u16 end; }` represents contiguous ranges of externally visible pin numbers. `core.c` computes these ranges and both pinctrl/GPIO paths use them for pin-to-index and pin-range registration.
- `sh_pfc_register_gpiochip()` is implemented in `gpio.c` when GPIO support is built.
- `sh_pfc_register_pinctrl()` is implemented in the pinctrl glue file and registers the PFC with the Linux pinctrl subsystem.
- `sh_pfc_read_raw_reg()`/`sh_pfc_write_raw_reg()` expose width-aware MMIO helpers for common and GPIO code.
- `sh_pfc_read()`/`sh_pfc_write()` expose 32-bit register access with physical-address translation and unlock handling.
- `sh_pfc_get_pin_index()` maps a hardware pin number into `info->pins[]` index space.
- `sh_pfc_config_mux()` programs mux fields for a mark and pinmux type.

## Control Flow And Integration
This header is included by the core implementation and helper layers. It creates the internal contract: `core.c` owns MMIO mapping, mux programming, and register helpers; `pinctrl.c` uses `sh_pfc_config_mux()` to apply mux states; `gpio.c` uses pin indexing and raw register helpers to implement GPIO get/set/direction integration.

## State And Persistence
The header owns no storage. It defines the shape of pin range state embedded in `struct sh_pfc` and exposes functions that mutate hardware registers or use the `struct sh_pfc` runtime object.

## Dependencies
It includes `<linux/types.h>` for integer types and local `sh_pfc.h` for `struct sh_pfc` and SoC metadata definitions.

## Risks And Review Notes
- Because this is an internal cross-file API, signature changes require synchronized updates in `core.c`, `gpio.c`, and pinctrl glue.
- `struct sh_pfc_pin_range` uses `u16`; SoCs with pin numbers beyond 65535 would need a type expansion.
- Callers must ensure `struct sh_pfc` has been initialized by the core before using helpers; the header does not encode lifecycle constraints.

## Test Signals
Build tests with `CONFIG_PINCTRL_SH_PFC` and `CONFIG_PINCTRL_SH_PFC_GPIO` catch prototype drift. Runtime pinmux and GPIO tests indirectly validate that the shared helpers operate with the expected `struct sh_pfc` state.
