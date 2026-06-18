# sources/distributed-fs/ceph-client/drivers/clk/clk-asm9260.c

## Purpose
Registers the AlphaScale ASM9260 clock controller at early OF init. It builds a clock tree from a fixed PLL rate register, muxes, mux update gates, one-based dividers, and AHB peripheral gates.

## Important APIs, Types, And Functions
Descriptor types are `asm9260_div_clk`, `asm9260_gate_data`, and `asm9260_mux_clock`. Static tables define divider clocks, mux gates, AHB gates, parent data, mux tables, and mux clocks. The entry is `asm9260_acc_init`, declared with `CLK_OF_DECLARE`.

## Control Flow
Initialization allocates onecell data, maps the controller with `of_io_request_and_map`, reads the SYSPLL rate from register bits times 1 MHz, registers a fixed-rate PLL, registers muxes with table encodings, registers mux update gates, registers dividers into binding-indexed slots, registers AHB gates into binding-indexed slots, checks leaf slots for `ERR_PTR`, and adds the OF provider.

## State And Persistence
Static globals hold `clk_data`, MMIO `base`, and a spinlock. Hardware registers persist mux selection, update gate bits, divider values, and AHB gates. Registered clocks are permanent early-boot objects.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/alphascale,asm9260.h`, CCF mux/gate/divider helpers, OF early init, and parent clocks from DT index 0 plus named PLL/RTC parents.

## Risks And Edge Cases
Several registration calls are not individually checked before later leaf-slot validation, and intermediate mux/gate failures may be missed. Failure paths use `panic` for mapping or PLL registration failures. The fixed PLL rate assumes register bits encode MHz directly.

## Test Signals
Boot with ASM9260 DT, verify PLL rate from `HW_SYSPLLCTRL`, all binding indexes resolve, mux table values `{0,1,3}` select expected parents, one-based divider rates are correct, and `CLK_IGNORE_UNUSED` gates stay enabled.
