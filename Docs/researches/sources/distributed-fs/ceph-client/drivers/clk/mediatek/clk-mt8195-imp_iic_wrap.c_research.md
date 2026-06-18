# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-imp_iic_wrap.c

## Purpose
`clk-mt8195-imp_iic_wrap.c` registers MT8195 I2C wrapper clocks for south and west wrapper regions.

## Important APIs, Types, And Functions
It defines `imp_iic_wrap_cg_regs`, `imp_iic_wrap_s_clks`, `imp_iic_wrap_w_clks`, descriptors for south and west wrappers, and OF matches `mediatek,mt8195-imp_iic_wrap_s` and `mediatek,mt8195-imp_iic_wrap_w`.

## Control Flow, State, And Persistence
The simple probe registers region-specific I2C wrapper gates and publishes a onecell provider. No custom state is maintained.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are I2C controllers in the south and west infrastructure regions. Risks include region mismatch and wrong wrapper parent clocks producing adapter probe failures. Test signals include I2C bus probe/transfer in both regions, runtime PM, and unused-clock cleanup.
