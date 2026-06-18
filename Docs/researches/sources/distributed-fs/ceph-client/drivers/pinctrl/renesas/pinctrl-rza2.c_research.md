# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza2.c

## Purpose

This file implements the combined pinctrl and GPIO driver for the Renesas RZ/A2 R7S9210 family. It provides runtime DT parsing, pinctrl group/function registration, GPIO operations for all SoC pins, and direct programming of RZ/A2 PFC/PDR/PMR/PFS registers.

## Important APIs, Types, And Functions

The main private state is `struct rza2_pinctrl_priv`, which holds the device, MMIO base, pin descriptors, pinctrl descriptor/device, one GPIO range, pin count, and a mutex for generic group/function registration. Important functions include `rza2_set_pin_function()`, `rza2_pin_to_gpio()`, GPIO callbacks `rza2_chip_get_direction()`, `rza2_chip_direction_input()`, `rza2_chip_get()`, `rza2_chip_set()`, `rza2_chip_direction_output()`, registration helpers `rza2_gpio_register()` and `rza2_pinctrl_register()`, DT parser `rza2_dt_node_to_map()`, mux callback `rza2_set_mux()`, and `rza2_pinctrl_probe()`.

## Control Flow

`core_initcall(rza2_pinctrl_init)` registers the platform driver. Probe allocates `rza2_pinctrl_priv`, ioremaps the PFC resource, initializes the mutex, derives `npins` from OF match data times eight pins per port, fills the pinctrl descriptor, and calls `rza2_pinctrl_register()`. Registration creates pin descriptors from `rza2_gpio_names`, registers/enables pinctrl, validates `gpio-ranges`, registers one gpiochip covering all pins, and adds a single pinctrl GPIO range.

For pinctrl DT nodes, `rza2_dt_node_to_map()` requires a `pinmux` property. Each packed value uses low 16 bits as pin ID and high 16 bits as PSEL function value. The parser stores the pin list as a generic group and the PSEL array as function data, with group and function both named after the DT node. `rza2_set_mux()` later walks group pins and matching PSEL values, logs the target port/pin, and calls `rza2_set_pin_function()`.

`rza2_set_pin_function()` first puts the pin in Hi-Z/non-use by clearing its PDR field, temporarily switches PMR to GPIO, disables PFS write protection through PWPR, writes the PFS function with interrupt select cleared, restores write protection, and switches PMR back to peripheral mode. GPIO direction paths use `rza2_pin_to_gpio()` to set two-bit PDR fields to input or output; output direction writes PODR before driving the pin.

## State And Persistence

Driver-owned software state is devm-managed in `struct rza2_pinctrl_priv`. Dynamic pinctrl groups and functions are added to the generic pinctrl registries while DT nodes are parsed and protected by `priv->mutex`. The GPIO chip object is a file-scope static template mutated at registration time with label, parent, and `ngpio`, so the implementation assumes one active device instance. Hardware state is in PDR, PODR, PIDR, PMR, PFS, PWPR, and related PFC registers and persists only as SoC register state until reset or reconfiguration.

## Dependencies And Integration Points

The driver depends on Linux GPIO, platform, OF, pinctrl, and pinmux APIs plus internal `core.h` and `pinmux.h`. The supported compatible is `renesas,r7s9210-pinctrl`, with match data `22`, producing 176 pins across ports P0-PH and PJ-PM; port I is intentionally absent in `rza2_gpio_names` and `port_names`. Device tree must provide a matching top-level `gpio-ranges` covering all pins. Pinctrl clients use node-local `pinmux` arrays with packed pin/function values.

## Risks

There is little validation in `rza2_dt_node_to_map()`: pin IDs and function values from DT are not range-checked against `priv->npins` before later indexing `port_names` and programming registers. The file-scope static `gpio_chip chip` is mutated during registration and is not safe for multiple instances. Register writes are read-modify-write sequences without a spinlock around GPIO and mux paths, so concurrent consumers could race on shared port registers or the global PWPR write-protect sequence. `rza2_chip_get_direction()` changes hardware state by forcing Hi-Z pins to input as a side effect. The driver defines DSCR and other dedicated-pin registers but does not expose pinconf drive or dedicated-pin configuration.

## Test Signals

Useful validation includes build/probe for `renesas,r7s9210-pinctrl`, confirmation that 176 pins and the gpiochip register, GPIO direction/value tests across early numeric ports and lettered ports, pinmux tests for representative PSEL values, DT error tests for malformed `gpio-ranges`, robustness tests for out-of-range `pinmux` values, concurrent GPIO/mux stress around shared ports, and hardware readback of PWPR/PFS/PMR/PDR sequencing.
