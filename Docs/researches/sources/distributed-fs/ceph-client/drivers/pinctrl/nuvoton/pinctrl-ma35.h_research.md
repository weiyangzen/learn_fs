# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.h

## Purpose
This header defines the small contract between MA35 SoC-specific pin-table files and the common MA35 pinctrl implementation. It provides data structures and macros for declaring pins, their MFP register location, and their possible mux values, plus prototypes for the shared probe and PM helpers.

## Important APIs, types, and functions
`struct ma35_mux_desc` names one mux value. `struct ma35_pin_data` records the MFP register `offset`, field `shift`, and a null-terminated array of mux descriptors for one pin. `struct ma35_pinctrl_soc_info` carries a SoC pin table, pin count, and `get_pin_num()` callback. `MA35_PIN()` builds a `struct pinctrl_pin_desc` with compound-literal driver data, and `MA35_MUX()` builds one mux descriptor. The declared functions are `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()`.

## Control flow
The header has no executable flow. At compile time, `MA35_PIN()` expands SoC data into pinctrl descriptors. At runtime, the common driver receives a `ma35_pinctrl_soc_info`, publishes the descriptors to pinctrl core, and uses the SoC `get_pin_num()` callback to translate device-tree MFP offset/shift triples back to pin numbers.

## State and persistence behavior
The macro-created pin and mux descriptors are static immutable SoC data. The `drv_data` field points at compound-literal `struct ma35_pin_data` storage associated with each descriptor. Persistent hardware state is not changed by the header itself; register writes happen in `pinctrl-ma35.c`.

## Dependencies and integration points
It includes generic pinconf, pinmux, and platform-device headers. It is included by `pinctrl-ma35.c` and `pinctrl-ma35d1.c`. The macro format is coupled to the common driver's expectation that each pin has a register offset, bit shift, and mux metadata, even though current mux programming is driven by device-tree triples rather than by searching the per-pin mux list.

## Risks
Macro misuse is the main risk. The `MA35_PIN()` compound literals must remain valid for static descriptor lifetime; using the macro in automatic storage would be unsafe. The `get_pin_num()` callback must match the SoC's MFP register layout, or parsed groups will refer to the wrong pinctrl pin numbers. Mux descriptor names are useful documentation and potential debug data, but they do not independently validate device-tree mux values.

## Test signals
Build tests catch prototype and macro syntax drift. Runtime pinctrl debugfs output should show the SoC pin names from `MA35_PIN()`. Device-tree group parsing that maps MFP offset/shift triples to expected pin names validates the `ma35_pinctrl_soc_info` contract.
