# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.c

## Purpose
This file implements reusable Aspeed pinmux expression evaluation. It lets common or SoC-specific mux code ask whether a signal descriptor or full signal expression is currently enabled or disabled in hardware.

## Important APIs, types, and functions
`aspeed_sig_desc_eval()` reads a descriptor bitfield from the selected IP regmap and compares it against either the descriptor's enable or disable value. `aspeed_sig_expr_eval()` evaluates all descriptors in an expression, unless the SoC provides a custom `ctx->ops->eval`. `aspeed_sig_desc_print_val()` is a debug helper showing desired and actual register state. `aspeed_pinmux_ips` maps IP indices to debug names for SCU, GFX, and LPC.

## Control flow
Expression evaluation starts in callers such as `aspeed_sig_expr_enable()`, `aspeed_sig_expr_disable()`, or SoC-specific post-write verification. If a custom eval op exists, `aspeed_sig_expr_eval()` delegates to it. Otherwise it loops through every descriptor in the expression and calls `aspeed_sig_desc_eval()` against `ctx->maps[desc->ip]`. The expression returns true only if every descriptor matches the requested enabled or disabled state. A zero result stops evaluation early as false; a negative result propagates regmap or missing-map errors.

## State and persistence behavior
This file does not mutate hardware and has no persistent state. It reads regmap-backed hardware registers and interprets their current values. Debug messages expose register values but do not affect state.

## Dependencies and integration points
It depends on `pinmux-aspeed.h`, Linux regmap, bit operations such as `__ffs()`, and kernel debug logging. It is called by `pinctrl-aspeed.c` for enable/disable decisions and by AST2600 code to verify writes. It supports multiple register-map domains through `ASPEED_IP_SCU`, `ASPEED_IP_GFX`, and `ASPEED_IP_LPC`.

## Risks
The code assumes descriptor masks are nonzero because it calls `__ffs(desc->mask)`. Missing regmaps return `-ENODEV`, which can break muxing for descriptors targeting IP domains not installed by a SoC driver. Multi-bit descriptor semantics require explicit enable and disable values; a field value that is neither returns false for both states and can leave callers needing additional handling. Debug indexing assumes `desc->ip` is in range of `aspeed_pinmux_ips`.

## Test signals
Unit-style tests can exercise descriptor comparison on fake regmaps for single-bit, multi-bit, enabled, disabled, and neither-state values. Runtime validation comes from successful muxing paths and from dynamic debug traces showing expected register fields. Negative tests should cover missing maps and invalid or protected register access failures.
