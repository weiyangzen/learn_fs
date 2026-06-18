# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.h

## Purpose
This header defines the Aspeed data-driven pinmux model and the macro system used by SoC files to describe complex pin priority, signal, group, and function relationships. It captures why Aspeed muxing cannot be represented as a simple one-bit-per-function model.

## Important APIs, types, and functions
Core types are `struct aspeed_sig_desc`, `struct aspeed_sig_expr`, `struct aspeed_pin_desc`, `struct aspeed_pin_group`, `struct aspeed_pin_function`, `struct aspeed_pinmux_ops`, and `struct aspeed_pinmux_data`. IP IDs `ASPEED_IP_SCU`, `ASPEED_IP_GFX`, and `ASPEED_IP_LPC` index the regmap array. Descriptor macros include `SIG_DESC_IP_BIT`, `SIG_DESC_BIT`, `SIG_DESC_SET`, `SIG_DESC_CLEAR`, and list/expression declaration macros. Pin macros such as `PIN_DECL_1`, `PIN_DECL_2`, `PIN_DECL_3`, `PIN_DECL_4`, `SSSF_PIN_DECL`, and `GPIO_PIN_DECL` build priority arrays. Group/function macros build arrays consumed by pinctrl callbacks. `aspeed_sig_expr_set()` is an inline wrapper around the SoC `set` operation.

## Control flow
SoC files use the macros to create descriptor arrays, expression objects, expression pointer lists, per-pin priority arrays, group pin arrays, and function group lists. At runtime, common mux code walks `aspeed_pin_desc.prios` from highest to lowest priority, evaluates or disables expression lists, and then calls the SoC `set` op for the target expression. The model supports AND across descriptors in one expression, OR across expressions in one signal priority, and priority ordering across signals on the same pin.

## State and persistence behavior
The header creates static const data in including C files. Runtime mutable state is limited to `struct aspeed_pinmux_data`, especially installed regmaps and optional ops. Hardware state lives outside the header in the selected IP registers. Descriptors store enable and disable patterns, not current state.

## Dependencies and integration points
The header depends on Linux regmap and bit macros and is included by both shared Aspeed implementation files and SoC-specific pin table files. It integrates with the Linux pinctrl core indirectly through `pinctrl-aspeed.h`, whose data structures include `struct aspeed_pinmux_data`. It also encodes compile-time validation strategy through generated symbol names and aliases.

## Risks
The macro layer is dense and easy to misuse. Naming errors can either intentionally fail compilation through duplicate symbols or accidentally create wrong but valid function/group relationships. The model relies on correct priority order and complete higher-priority disable lists to make lower-priority signals and GPIO work. `SIG_DESC_CLEAR` sets both enable and disable to zero for clear-selected descriptors, which is appropriate only for hardware fields where zero is both selected state and safe disabled comparison. The header documents many hardware corner cases, so changes that simplify it risk breaking valid mux cases.

## Test signals
Compile-time coverage is important because symbol aliases and designated initializers catch many table mistakes. Runtime tests should target representative corner cases from the header comments: shared bits, multiple descriptors, multiple expressions for one signal, strap-influenced signals, non-GPIO "other" functions, and GPIO as non-default or input-only signals. Debug traces from `pinmux-aspeed.c` can confirm descriptor interpretation.
