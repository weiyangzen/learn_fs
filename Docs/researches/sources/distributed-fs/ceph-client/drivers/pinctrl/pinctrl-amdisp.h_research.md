# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.h

Purpose: Defines the static data used by the AMD ISP pinctrl driver: three pins, three one-pin groups, GPIO range pins/names, and one GPIO function descriptor.

Important APIs and types: `amdisp_pins[]` declares `GPIO_0`, `GPIO_1`, and `GPIO_2` with comments identifying sensor control roles. `amdisp_range_pins[]` and `amdisp_range_pins_name[]` describe the gpiochip range. `enum amdisp_functions`, `struct amdisp_function`, `amdisp_functions[]`, `struct amdisp_pingroup`, and `amdisp_groups[]` provide the pinctrl group/function data consumed by `pinctrl-amdisp.c`.

Control flow: The header has no executable flow. Macros `AMDISP_GPIO_PINS()`, `FUNCTION()`, and `PINGROUP()` generate the static arrays that probe wires into the pinctrl descriptor and gpio range.

State and persistence: All data is immutable. Hardware persistence is controlled by the C file after a consumer sets one of the GPIO lines.

Dependencies and integration points: Relies on pinctrl descriptor types and `ARRAY_SIZE()` from kernel headers included by the C file. It is intentionally local and not guarded by include guards because only `pinctrl-amdisp.c` includes it.

Risks: `struct amdisp_pingroup.funcs` is typed as `unsigned int *` but initialized with an `(int[])` compound literal; this works in practice for static data but is unnecessarily loose. Function data is not used by a `pinmux_ops` implementation in the C file, so the function table is descriptive rather than active.

Test signals: Build coverage, pinctrl debugfs group listing, gpio line names `gpio0`-`gpio2`, and matching `ngpio`/range sizes validate the header tables.
