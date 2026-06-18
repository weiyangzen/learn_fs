# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-bm1880.c

## Purpose
This platform driver implements pinctrl, pinmux, and pinconf for the Bitmain BM1880 SoC. It describes 112 MIO pins, a large table of peripheral groups and functions, and packed MMIO register programming for mux selection, pull controls, Schmitt input, slew rate, and drive strength.

## Important APIs, Types, and Functions
`struct bm1880_pinctrl` stores MMIO base, pinctrl device, group table, function table, and per-pin drive-width data. `struct bm1880_pctrl_group` and `struct bm1880_pinmux_function` describe groups/functions. `struct bm1880_pinconf_data` holds the drive strength bit width per pin. The table macros are `BM1880_PINCTRL_GRP`, `BM1880_PINMUX_FUNCTION`, and `BM1880_PINCONF_DAT`. Operational callbacks include group accessors, `bm1880_pinmux_set_mux`, `bm1880_pinconf_drv_set`, `bm1880_pinconf_drv_get`, `bm1880_pinconf_cfg_get`, `bm1880_pinconf_cfg_set`, and `bm1880_pinconf_group_set`. Probe is `bm1880_pinctrl_probe`, registered at `arch_initcall`.

## Control Flow and State
Probe allocates state, maps the platform resource, binds static group/function/pinconf arrays, registers the static pinctrl descriptor, stores drvdata, and logs initialization. Muxing iterates each pin in the selected group; each register word covers two pins, so it calculates `offset = (pin >> 1) << 2` and per-pin mux field offset before clearing and writing a 2-bit selector. Pinconf reads/writes the same register word and uses macros to locate pull, drive, Schmitt, and slew fields for the selected pin. Group pinconf applies the same configs to all pins in the group.

## State and Persistence Behavior
All persistent state is in the BM1880 pinctrl MMIO register block at `BM1880_REG_MUX` plus per-pin offsets. Static tables are immutable. There is no explicit locking around relaxed read/modify/write sequences, so concurrent pinctrl operations could theoretically race if applied to different fields in the same word. Drive strength encoding supports two pin classes: 3-bit fields for 4-32 mA and 2-bit fields for 4-16 mA.

## Dependencies and Integration Points
The driver integrates with platform bus and OF compatible `bitmain,bm1880-pinctrl`, Linux pinctrl core, generic pinconf DT parsing, and pinctrl utils. It does not register a gpiochip; GPIO mode is represented as pinmux functions for pins that can be muxed to GPIO controllers elsewhere.

## Risks
The large hand-maintained static mapping tables are the primary risk. Any wrong pin number, group membership, mux value, or drive-width entry will produce board-level pin failures. `bm1880_pinconf_cfg_get` passes a boolean bit value into `bm1880_pinconf_drv_get`, which cannot recover multi-bit drive strength values for 3-bit fields, so drive-strength get appears lossy. Pull-up, pull-down, and bias-disable set paths only set bits and do not clear mutually exclusive fields, which relies on hardware semantics or may leave conflicting state. Relaxed unlocked RMW can lose adjacent-field updates.

## Test Signals
Validation should cover registration on BM1880 DT, muxing representative peripherals such as NAND, SDIO, Ethernet, I2C, UART, PWM, I2S, SPI, and GPIO groups, pinconf set/get for both drive-width classes, group pinconf propagation, and stress cases where two consumers update different fields in the same register word.
