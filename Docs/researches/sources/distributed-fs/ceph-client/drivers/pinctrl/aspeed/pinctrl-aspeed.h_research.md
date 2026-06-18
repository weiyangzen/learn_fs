# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.h

## Purpose
This header defines the common Aspeed pinctrl data model shared between SoC-specific pin table files and the common implementation. It bridges Linux pinctrl descriptors, Aspeed pinmux expressions, SCU regmap access, and generic pinconf support.

## Important APIs, types, and functions
`struct aspeed_pin_config` describes one pinconf-capable hardware bitfield for a parameter, pin range, register, and mask. `struct aspeed_pin_config_map` maps generic pinconf parameter/argument pairs to hardware values and masks. `struct aspeed_pinctrl_data` is the central per-SoC data carrier: SCU regmap, pin descriptors, pin config entries, pinmux data, and config maps. Macros `ASPEED_PINCTRL_PIN`, `ASPEED_SB_PINCONF`, `ASPEED_PULL_DOWN_PINCONF`, and `ASPEED_PULL_UP_PINCONF` reduce boilerplate in SoC files. The header prototypes all common Aspeed group, function, mux, GPIO, probe, and pinconf operations.

## Control flow
SoC files include this header to construct static `aspeed_pinctrl_data` instances and pin descriptor arrays. During probe, those instances are passed to `aspeed_pinctrl_probe()`. After registration, Linux pinctrl callback tables in the SoC file call the functions declared here, which read back the same data structures through `pinctrl_dev_get_drvdata()`.

## State and persistence behavior
The header itself stores no state. It defines how state is represented: hardware state is reached through `struct regmap *scu`, static SoC capabilities are represented by const arrays, and mux state is represented by `struct aspeed_pinmux_data`. Pinconf map entries are immutable lookup tables. The macros create static data whose lifetime is the kernel image lifetime.

## Dependencies and integration points
The header depends on Linux `pinctrl`, `pinmux`, `pinconf`, generic pinconf, `regmap`, and the Aspeed pinmux header. It is included by common Aspeed implementation files and SoC-specific drivers. Its function prototypes are the integration contract used when constructing `struct pinctrl_ops`, `struct pinmux_ops`, and `struct pinconf_ops`.

## Risks
Macro-generated `drv_data` points at `PIN_SYM(name_)`, so every pin descriptor must have a matching pin declaration symbol. Pin range entries in `aspeed_pin_config` are inclusive and rely on numeric pin ordering matching hardware banks. Config map wildcard entries can make lookup order significant. Because this header exposes internal helper prototypes rather than an opaque interface, SoC files can accidentally couple to assumptions in the common implementation.

## Test signals
Build coverage is the main signal: missing pin symbols, bad macro use, type mismatches, or duplicate declarations should fail compilation. Runtime tests come through SoC drivers using these helpers and should verify that pin descriptor `drv_data` resolves to the expected `aspeed_pin_desc` and that pinconf ranges map to the intended pins.
