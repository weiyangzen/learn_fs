# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza1.c

## Purpose

This file implements the combined pinctrl and GPIO driver for Renesas RZ/A1-family SoCs, including RZ/A1H, RZ/A1M, and RZ/A1L variants. Unlike the older SuperH table-only files, this driver parses device-tree pinmux nodes at runtime, registers dynamic pin groups/functions, exposes per-port GPIO chips, and programs RZ/A1 port registers directly.

## Important APIs, Types, And Functions

Key types are `struct rza1_bidir_pin`, `struct rza1_bidir_entry`, `struct rza1_swio_pin`, `struct rza1_swio_entry`, `struct rza1_pinmux_conf`, `struct rza1_mux_conf`, `struct rza1_port`, and `struct rza1_pinctrl`. Important static SoC data includes `rza1h_pmx_conf` and `rza1l_pmx_conf`, selected by OF compatible data.

Important functions include `rza1_pinmux_get_flags()`, `rza1_set_bit()`, `rza1_pin_reset()`, `rza1_pin_set_direction()`, `rza1_pin_mux_single()`, GPIO callbacks such as `rza1_gpio_request()`, `rza1_gpio_direction_input()`, `rza1_gpio_direction_output()`, `rza1_gpio_get()`, and `rza1_gpio_set()`, DT parsing functions `rza1_dt_node_pin_count()`, `rza1_parse_pinmux_node()`, `rza1_dt_node_to_map()`, mux callback `rza1_set_mux()`, GPIO registration helpers, `rza1_pinctrl_register()`, and `rza1_pinctrl_probe()`.

## Control Flow

`core_initcall(rza1_pinctrl_init)` registers a platform driver. Probe allocates `struct rza1_pinctrl`, ioremaps the first resource, initializes the mutex, stores OF match data for the variant-specific bidirectional/SWIO tables, fills a `pinctrl_desc`, then calls `rza1_pinctrl_register()`.

Registration creates 192 pin descriptors named `P<port>-<pin>`, initializes 12 `struct rza1_port` instances with per-port spinlocks, registers and enables pinctrl, then scans GPIO child nodes. Each GPIO child must provide `gpio-ranges`; `rza1_parse_gpiochip()` registers a devm GPIO chip for the matching port and adds a pinctrl GPIO range.

When a pinctrl DT node is parsed, `rza1_dt_node_to_map()` counts pins either in the node or in child subnodes, allocates mux configs and group pins, and calls `rza1_parse_pinmux_node()`. That parser reads packed `pinmux` values, decodes low 16 bits as pin ID and high 16 bits as mux function, validates port/pin bounds, and derives optional SWIO direction flags from generic pinconf properties such as `input-enable`, `output-enable`, and legacy `PIN_CONFIG_LEVEL`. The driver then registers a generic group and a generic function with identical names. `rza1_set_mux()` later retrieves the stored `rza1_mux_conf` array and calls `rza1_pin_mux_single()` per pin.

`rza1_pin_mux_single()` resets the pin to GPIO input-buffer-disabled state, merges DT flags with variant tables, optionally enables bidirectional mode, translates DT mux functions 1-8 into register values 0-7, writes PFC/PFCE/PFCEA selection bits, handles SWIO pins through PM instead of PIPC, and finally enables alternate mode through PMC.

## State And Persistence

Persistent software state for the device is devm-managed under `struct rza1_pinctrl`: base address, pin descriptors, port descriptors, the pinctrl device, and variant match data. Dynamic groups/functions added while parsing DT nodes are stored in the pinctrl generic registries; a mutex serializes those additions. Per-port spinlocks protect read-modify-write sequences on 16-bit port registers. Hardware pin state lives in `P`, `PPR`, `PM`, `PMC`, `PFC`, `PFCE`, `PFCEA`, `PIBC`, `PBDC`, and `PIPC` registers and is not persisted across reset by this file.

## Dependencies And Integration Points

The driver depends on Linux platform, OF, fwnode, GPIO, pinctrl, pinmux, and generic pinconf APIs. It includes internal pinctrl headers `core.h`, `devicetree.h`, `pinconf.h`, and `pinmux.h`. OF compatibles are `renesas,r7s72100-ports` for RZ/A1H/M and `renesas,r7s72102-ports` for RZ/A1L. Integration with clients is DT-driven through `pinmux` and `gpio-ranges`; GPIO consumers use the per-port gpiochips, and pinctrl consumers use dynamically created node-named mux groups/functions.

## Risks

The variant flag tables are hand-maintained and easy to desynchronize from hardware manuals. There is a notable table entry risk in `rza1l_bidir_entries`: the port 5 row uses `ARRAY_SIZE(rza1l_bidir_pins_p4)` while pointing at `rza1l_bidir_pins_p5`, which can truncate or otherwise mismatch the intended bidirectional list. DT mux functions must be encoded from 1 to 8; zero would underflow before register programming. `rza1_dt_node_to_map()` uses devm allocations for groups/functions that can live for the device lifetime, which is acceptable but means malformed repeated nodes can consume memory until device removal. GPIO free resets direction and input buffer state, which can surprise clients expecting last output value retention. Missing or malformed `gpio-ranges` prevents that GPIO child from registering.

## Test Signals

Good tests include build and probe coverage for both compatibles, pinctrl debugfs inspection of 192 pins and dynamically parsed groups, DT parsing tests for flat and child-subnode `pinmux` layouts, mux tests for normal, bidirectional, and SWIO pins, GPIO request/free/direction/value tests per port, validation that output readback works through PBDC/PPR, error-path tests for invalid packed pin IDs and malformed `gpio-ranges`, and hardware tests around the RZ/A1L port 5 bidirectional table.
