# sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock5.c

## Purpose
`clk-versaclock5.c` is an I2C CCF driver for IDT/Renesas VersaClock 5 and VersaClock 6 clock-generator families. It exposes one selectable input path, optional frequency doubler, PFD, fractional PLL, up to four fractional output dividers (FODs), and up to five output buffers. It supports multiple models with different output counts, internal crystal availability, PFD doubler support, FOD sync-bypass capability, and maximum VCO frequencies.

## Important APIs, Types, And Functions
`struct vc5_chip_info` captures model-specific hardware capacity and flags. `struct vc5_driver_data` owns the I2C client, regmap, input clocks, clock mux/doubler/PFD/PLL nodes, FOD array, and output array. `struct vc5_hw_data` stores PLL/FOD CCF state and cached integer/fractional divider fields. `struct vc5_out_data` stores output CCF state plus pending DT-derived electrical configuration masks.

The major operations are `vc5_mux_*` for selecting `xin` versus `clkin`, `vc5_dbl_*` for optional reference doubling, `vc5_pfd_*` for PLL input predivision, `vc5_pll_*` for the 12-bit integer plus 24-bit fractional feedback divider, `vc5_fod_*` for the output divider's 12-bit integer plus fractional divider, and `vc5_clk_out_*` for output muxing and buffer enable. Device-tree parsing helpers include `vc5_update_mode()`, `vc5_update_power()`, `vc5_update_slew()`, `vc5_map_cap_value()`, `vc5_update_cap_load()`, and `vc5_get_output_config()`.

## Control Flow
Probe allocates per-device state, reads optional `xin` and `clkin` parent clocks, initializes a protected regmap that blocks writes to factory-reserved registers, applies optional shutdown/output-enable polarity bits, and builds the CCF graph in dependency order. If no external `xin` exists but the model has `VC5_HAS_INTERNAL_XTAL`, it registers a fixed 25 MHz internal crystal. For external crystals, it optionally programs load capacitance from `idt,xtal-load-femtofarads`.

The registered tree is input mux, optional doubler, PFD, PLL, FODs, a special OUT0 path, and FOD-connected outputs. `vc5_map_index_to_output()` handles package-specific output numbering, notably the 5P49V5933 sparse mapping. Output registration also reads child nodes named `OUTn` for mode, voltage, and slew settings, but those settings are applied lazily in `vc5_clk_out_prepare()` when the output buffer is enabled. The OF clock provider returns only output clocks, not internal PLL/FOD nodes.

## State And Persistence
Persistent state lives in the chip's I2C registers: source enable bits, predivider configuration, PLL feedback fields, FOD divider blocks, FOD enable/source bits, output electrical configuration, output enable bits, and the global reset/sync trigger. Runtime state includes the regmap cache, optional fixed-rate internal crystal, CCF nodes, cached divider values staged by `determine_rate`, and per-output pending config masks. Suspend switches the regmap to cache-only and marks it dirty; resume turns bus access back on and syncs cached writes to hardware.

## Dependencies And Integration Points
The driver uses the Linux CCF, I2C, regmap, OF/property APIs, PM ops, and `dt-bindings/clock/versaclock.h` values for output modes. Board descriptions provide parent clocks named `xin` and/or `clkin`, optional top-level control properties (`idt,shutdown`, `idt,output-enable-active`, `idt,xtal-load-femtofarads`), and child output electrical properties. Clock consumers bind through the OF provider and output indexes.

## Risks
FOD and PLL rate calculations rely on integer arithmetic, shifted fractional fields, and cached `determine_rate` results, so changes can easily introduce off-by-one rate errors. `vc5_fod_determine_rate()` warns that one divider combination silences the output and clamps to avoid it; relaxing that logic is risky. `vc5_clk_out_prepare()` may write reserved sync-bypass registers on supported VC6E devices and toggles global reset after FOD updates, both of which are hardware-sensitive sequences. The driver mixes devm-managed clocks with manually registered fixed-rate internal crystal and manual provider removal, so error paths must keep ownership balanced. Output child-node lookup by `OUT%d` uses hardware output numbering; mismatches in DT naming silently skip electrical configuration. Rate and divider arithmetic uses `unsigned long` and `u32` near multi-GHz VCO values, which is safer on 64-bit targets than 32-bit ones.

## Test Signals
Key tests include probe for all listed I2C/OF compatibles, input mux behavior with only `xin`, only `clkin`, both inputs, and internal crystal fallback, and clock-rate requests spanning PFD bypass/division, optional doubler, PLL fractional feedback, and FOD fractional output division. DT validation should cover legal and illegal output modes, voltages, slew percentages, load-capacitance bounds, and 5P49V5933 index mapping. Runtime validation should verify suspend/resume restores register state, output prepare/unprepare toggles buffer enable, FOD sync bypass prevents unrelated output glitches on VC6E variants, and unsupported factory-reserved register writes remain blocked by regmap.
