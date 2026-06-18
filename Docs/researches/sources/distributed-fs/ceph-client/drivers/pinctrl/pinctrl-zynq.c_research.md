# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynq.c

## Purpose
Implements the classic Xilinx Zynq pinctrl, pinmux, and pinconf driver for 54 MIO pins plus EMIO SD card-detect/write-protect pseudo pins. Static tables model all supported groups and functions, while register access goes through a syscon regmap.

## Important APIs, Types, And Functions
Core types are `struct zynq_pinctrl`, `struct zynq_pctrl_group`, and `struct zynq_pinmux_function`. Important functions include `zynq_pinmux_set_mux()`, `zynq_pinconf_cfg_get()`, `zynq_pinconf_cfg_set()`, `zynq_pinconf_group_set()`, and `zynq_pinctrl_probe()`. The driver defines custom `PIN_CONFIG_IOSTANDARD` plus generic pinconf parameters for bias, slew, power source, and low-power receiver disable.

## Control Flow
Probe looks up a `syscon` phandle, uses the platform memory resource start as the pinctrl register offset, assigns static group/function tables, and registers the pinctrl descriptor. Pinmux maps a requested function/group either by writing per-pin mux bits in each MIO register or, for SDIO CD/WP functions, by writing dedicated selector fields. Pinconf get/set reads the target MIO register, interprets or updates tristate, pull-up, speed, IO standard, power source, and receiver-disable bits, then writes the register back.

## State And Persistence
Hardware state persists in the syscon register block. Driver state is devm-managed `struct zynq_pinctrl` with pointers to static group and function tables. EMIO pins are present for SDIO CD/WP mux selection but normal pinconf rejects pins beyond `ZYNQ_NUM_MIOS`.

## Dependencies And Integration Points
Integrates with DT compatible `xlnx,pinctrl-zynq`, the syscon provider, generic DT pinconf parsing through `pinconf_generic_dt_node_to_map_all`, and `pinctrl_utils_free_map`. It participates in the kernel pinctrl, pinmux, and generic pinconf APIs.

## Risks
The large static tables must match Zynq silicon mux encodings exactly. Group names with SDIO card-detect/write-protect pseudo pins have special register behavior unlike normal mux groups. Invalid IO-standard warnings print the parameter value rather than the invalid argument, reducing diagnostics. Register read/write errors are collapsed to `-EIO` in pinconf paths.

## Test Signals
Use DT states for representative Ethernet, USB, SDIO, SPI, UART, I2C, GPIO, and SDIO CD/WP functions; verify syscon register writes; test pinconf readback for supported parameters; and run compile tests with `CONFIG_PINCTRL_ZYNQ`.
