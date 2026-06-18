# Research: subset-b-005107 Renesas pinctrl source files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7757.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7757.c

## Purpose

This file is the SuperH SH7757 B0-step pin-function-controller description consumed by the shared Renesas `sh_pfc` core. It is a declarative SoC map: it names GPIO-capable pins from ports PTA through PTZ, describes input/output/function selector IDs, maps alternate-function marks to pins, lists exported function GPIO names, and publishes the register layout through `sh7757_pinmux_info`.

## Important APIs, Types, And Functions

The central API surface is the exported `const struct sh_pfc_soc_info sh7757_pinmux_info`. Important tables are the large enum ranges bounded by `PINMUX_DATA_BEGIN/END`, `PINMUX_INPUT_BEGIN/END`, `PINMUX_OUTPUT_BEGIN/END`, and `PINMUX_FUNCTION_BEGIN/END`; `pinmux_data`; `pinmux_pins`; `pinmux_func_gpios`; `pinmux_config_regs`; and `pinmux_data_regs`. The implementation relies on `sh_pfc.h` macros such as `PINMUX_DATA()`, `PINMUX_GPIO()`, `GPIO_FN()`, `PINMUX_CFG_REG()`, `PINMUX_CFG_REG_VAR()`, `PINMUX_DATA_REG()`, and `GROUP()`.

## Control Flow

There is no executable probe or callback code in this source. Board or CPU setup code references `sh7757_pinmux_info`, and the shared `sh_pfc` driver uses the static tables to register pins, function GPIOs, mux choices, and data registers. Runtime pin selection in the core resolves requested marks through `pinmux_data`, programs the port control registers in `pinmux_config_regs`, and reads or writes GPIO data through `pinmux_data_regs`.

## State And Persistence

All file-owned state is static constant data. Persistent runtime state is hardware register state in the PFC block, not state stored by this file. Register values remain until reset, power loss, or a later pinctrl/GPIO operation changes the same fields. The disabled `PPCR` config block under `#if 0` is source state only and is not exposed to the core.

## Dependencies And Integration Points

The file depends on `<cpu/sh7757.h>` for SoC mark and GPIO IDs and on the Renesas `sh_pfc` common model. It describes direct MMIO register addresses around `0xffec0000` through `0xffec0084`: per-port control registers `PACR` through `PZCR`, selector registers `PSEL0` through `PSEL8`, and data registers `PADR` through `PZDR`. Covered peripheral signals include memory bus, MMC/SD, SCIF/COM serial, I2C/DDC, SGPIO, USB VBUS, JTAG/debug, audio, PWM, LPC-like signals, event inputs, SIM, SPI, and on-chip NAND/data pins.

## Risks

The main risk is table correctness. Enum order, `PINMUX_DATA()` associations, function GPIO ordering, register addresses, bit widths, and reserved-field padding must match the SH7757 hardware manual exactly. Several ports have missing top bits, and the config tables use zero placeholders for reserved fields that the common core must not program. The `PPCR` register is deliberately excluded while `PPDR` remains present, which can surprise GPIO coverage expectations for PTP pins. Incorrect selector entries in `PSEL0`-`PSEL8` would silently route a peripheral to the wrong alternate signal.

## Test Signals

Useful signals are build coverage for SH7757 PFC support, successful registration of `sh7757_pfc`, pinctrl debugfs listing of PTA-PTZ pins and function GPIOs, GPIO direction/value tests on ports with full and partial bit coverage, mux tests for high-value peripherals such as MMC, serial, I2C, SGPIO, USB VBUS, and memory bus signals, and readback tests confirming reserved fields are not modified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7757.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7785.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7785.c

## Purpose

This file supplies the SH7785 SoC-specific pinmux database for the Renesas/SuperH `sh_pfc` framework. It enumerates GPIO pins across ports PA through PR, records alternate-function marks for memory, serial, timer, display, audio, PCI, DMA, and interrupt signals, and exposes the PFC register map through `sh7785_pinmux_info`.

## Important APIs, Types, And Functions

The exported object is `const struct sh_pfc_soc_info sh7785_pinmux_info`. The important local data structures are the pinmux enum, `pinmux_data`, `pinmux_pins`, `pinmux_func_gpios`, `pinmux_config_regs`, and `pinmux_data_regs`. The file uses common `sh_pfc` declarative macros rather than defining local functions.

## Control Flow

Control flow is table-driven in the shared core. Once platform setup selects `sh7785_pinmux_info`, the common `sh_pfc` code uses the enum ranges to classify input, output, and function IDs; uses `pinmux_pins` and `pinmux_func_gpios` to expose GPIO/function names; uses `pinmux_data` to resolve mark-to-pin dependencies; and uses `pinmux_config_regs` and `pinmux_data_regs` to program or read the SH7785 PFC hardware.

## State And Persistence

This file owns no mutable software state. All arrays are static const, while mutable state lives in the common PFC driver and in hardware registers. Pinmux and GPIO settings persist only as MMIO register contents until reset, power loss, or later reconfiguration.

## Dependencies And Integration Points

The source depends on `<cpu/sh7785.h>` and `sh_pfc.h`. It maps control registers at `0xffe70000` and selector registers `P1MSELR`/`P2MSELR` at `0xffe70080`/`0xffe70082`; GPIO data registers are at `0xffe70020` through `0xffe7003e`. `PINMUX_CFG_REG_VAR()` is used for ports with sparse valid pins such as PE, PM, PP, PQ, and PR. The PFC data integrates with the generic pinctrl/GPIO view provided by the shared SuperH PFC core.

## Risks

Sparse ports and variable-width register descriptions are the high-risk areas: bad reserved counts in `PINMUX_CFG_REG_VAR()` would shift every later field in a register. Function GPIO entries must stay aligned with CPU header marks; a mismatch would make a valid-looking function program the wrong pin. PM, PP, PQ, and PR have partial data-register coverage, so board tests should not assume every nominal port bit is available. Selector registers with zeros in valid-looking positions need hardware-manual confirmation.

## Test Signals

Validation should include build coverage, successful `sh7785_pfc` registration, debugfs inspection of PA-PR pin names and function GPIOs, GPIO tests on full and sparse ports, mux tests for serial, IRQ, DMA, memory-bus, display/audio, and PCI-related signals, and register readback that confirms reserved fields remain untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7786.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7786.c

## Purpose

This source is the SH7786 pin-function-controller description for the `sh_pfc` common driver. It defines GPIO-capable pins for ports PA-PH and PJ, maps alternate functions for external bus, DMA, serial, SSI, flash/status, IRQ, and related SoC signals, and publishes the register tables as `sh7786_pinmux_info`.

## Important APIs, Types, And Functions

The only externally consumed object is `const struct sh_pfc_soc_info sh7786_pinmux_info`. Core data is carried in the enum ranges, `pinmux_data`, `pinmux_pins`, `pinmux_func_gpios`, `pinmux_config_regs`, and `pinmux_data_regs`. The file depends on `PINMUX_DATA`, `PINMUX_GPIO`, `GPIO_FN`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, and `PINMUX_DATA_REG` macros from the common Renesas PFC layer.

## Control Flow

There is no local runtime logic. The shared PFC driver receives `sh7786_pinmux_info` from SoC setup, registers the listed pins/functions, and programs the concrete control and data registers when pinctrl or GPIO clients request a mux, direction, or value change. The alternate-function selector registers `P1MSELR` and `P2MSELR` add another layer of table-driven choice for functions that share a pin.

## State And Persistence

All local tables are immutable. Runtime state is held by the shared PFC core and the SH7786 PFC hardware registers. The register state is volatile hardware configuration and is not saved by this file.

## Dependencies And Integration Points

Dependencies are `<cpu/sh7786.h>` and `sh_pfc.h`. The register map uses PFC control registers beginning at `0xffcc0000`, selector registers at `0xffcc0080` and `0xffcc0082`, and data registers from `0xffcc0020` to `0xffcc0030`. The source integrates with the SuperH PFC core, which exposes the data to Linux pinctrl and GPIO consumers.

## Risks

The SH7786 tables contain many sparse register fields: PE only exposes upper bits, PG only exposes bits 7-5, and PJ has bit 0 reserved in the config/data views. A wrong reserved placeholder or register width changes the semantic position of all following fields. The selector registers are dense and easy to misalign with enum IDs. Because the file has no validation code, errors appear only as incorrect board-level muxing or GPIO behavior.

## Test Signals

Good test signals are compile coverage, successful `sh7786_pfc` registration, debugfs presence of the expected PA-PJ pin set, GPIO direction/value tests on ports with sparse bits, mux validation for serial, SSI, flash/status, external bus, DMA, and IRQ signals, and hardware register readback for `P1MSELR`/`P2MSELR` choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7786.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-shx3.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-shx3.c

## Purpose

This file is the compact PFC description for the SH-X3 family. It maps ports PA-PH to GPIO and alternate-function marks for external data/address bus, DMA handshake, interrupt, serial, chip-select/status, and related signals, then exposes the whole description through `shx3_pinmux_info`.

## Important APIs, Types, And Functions

The exported integration object is `const struct sh_pfc_soc_info shx3_pinmux_info`. The relevant local arrays are `pinmux_data`, `pinmux_pins`, `pinmux_func_gpios`, `pinmux_config_regs`, and `pinmux_data_regs`. Like the other SuperH files in this group, it is purely declarative and uses the common `sh_pfc.h` macro language for pins, functions, config registers, and data registers.

## Control Flow

Runtime work is performed by the shared `sh_pfc` core after SoC setup selects `shx3_pinmux_info`. The core registers GPIO pins and function GPIOs, resolves mark dependencies with `pinmux_data`, writes control registers `PABCR`, `PCDCR`, `PEFCR`, and `PGHCR`, and reads or writes data through `PABDR`, `PCDDR`, `PEFDR`, and `PGHDR`.

## State And Persistence

The file owns only static const tables. Any mutable state is either common-core bookkeeping or the PFC hardware register contents. No suspend, restore, or persistence logic is implemented here.

## Dependencies And Integration Points

The source depends on `<cpu/shx3.h>` and `sh_pfc.h`. Unlike SH7757/SH7785/SH7786, it uses 32-bit grouped control and data registers that combine two ports per register, with explicit reserved padding in both config and data arrays. It integrates with Linux pinctrl/GPIO through the shared SuperH PFC driver.

## Risks

The compact 32-bit register packing is the primary risk. The ordering inside `GROUP()` must match the hardware bit order for both halves of each register, and PH has only pins 5-0 represented. Reserved high and interleaved bits in data registers must remain zero placeholders. Since this file is small and has no active checks, a single shifted entry could misconfigure multiple adjacent pins.

## Test Signals

Useful tests are build coverage, successful `shx3_pfc` registration, debugfs listing of PA-PH GPIOs and function GPIOs, GPIO read/write tests across each paired data register, mux tests for external bus, DMA, serial, IRQ, and chip-select/status functions, and readback that verifies reserved data bits are not exposed as usable GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza1.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza2.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rza2.c -->
