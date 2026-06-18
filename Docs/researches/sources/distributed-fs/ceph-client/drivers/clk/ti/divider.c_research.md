# sources/distributed-fs/ceph-client/drivers/clk/ti/divider.c

Purpose: TI divider clock implementation for standalone and composite component divider clocks. It parses DT divider properties, calculates masks/rates, programs divider registers, latches changes, and saves/restores context.

Important APIs/types/functions: exported `ti_clk_divider_ops`, `ti_clk_parse_divider_data()`, `of_ti_divider_clk_setup()`, and `of_ti_composite_divider_clk_setup()`. Key helpers include `_get_div()`, `_get_val()`, `ti_clk_divider_bestdiv()`, `ti_clk_divider_determine_rate()`, `ti_clk_divider_set_rate()`, and context save/restore callbacks.

Control flow: setup obtains the register address and bit shift, optional latch bit, index scheme flags, optional set-rate-parent flag, optional divider table, and min/max values. Runtime recalc reads the register field and converts it to a divisor. Determine-rate selects the best divisor, optionally asking the parent to round. Set-rate clamps the divisor, writes the encoded value, and pulses the latch bit if present.

State and persistence: each divider holds register location, shift, mask, min/max, optional table, latch, flags, and saved context. Hardware register fields persist across runtime; context callbacks preserve values across suspend/resume.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `ti_clk_latch()`, CCF rate APIs, DT properties `ti,dividers`, `ti,min-div`, `ti,max-div`, and component assembly through `ti_clk_add_component()`.

Risks: table allocation is permanent for registered clocks. Zero divisors return parent rate unless explicitly allowed, potentially masking bad hardware state. Best-divider search can alter parent rates when `CLK_SET_RATE_PARENT` is set, so parent capabilities matter.

Test signals: fixed divisor tables, one-based and power-of-two encodings, latch behavior, set-rate-parent cases, suspend/resume context restore, and invalid DT without `ti,max-div`.
