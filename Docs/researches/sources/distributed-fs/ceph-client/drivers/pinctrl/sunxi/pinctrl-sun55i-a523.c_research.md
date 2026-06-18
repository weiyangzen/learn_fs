# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523.c

Purpose: This is the built-in platform driver for the Allwinner SUN55I A523 pin controller. Unlike many older sunxi drivers in this set, it does not hard-code every pin/function table in C. It provides compact bank metadata to the generic DT-driven table builder in `pinctrl-sunxi-dt.c`, so the actual peripheral function groups come from child nodes in the device tree.

Important APIs, types, and data: The file defines `a523_nr_bank_pins`, listing implemented pin counts for banks PA through PK with PA absent and PB..PK present. `a523_irq_bank_map` maps ten interrupt-capable banks, and `a523_irq_bank_muxes` marks IRQ mux value 14 for PB..PK. `a523_pinctrl_data` is a `struct sunxi_pinctrl_desc` with `irq_banks`, `irq_bank_map`, `irq_read_needs_mux = true`, and `io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_SEL`. The probe calls `sunxi_pinctrl_dt_table_init()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT | SUNXI_PINCTRL_ELEVEN_BANKS`.

Control flow: Device-tree matching on `allwinner,sun55i-a523-pinctrl` binds `a523_pinctrl_driver`. `a523_pinctrl_probe()` passes the bank pin counts, per-bank IRQ mux values, descriptor, and register-layout flags to the DT table builder. The generated descriptor is then handed to the shared sunxi pinctrl core.

State and persistence: Runtime state is devm-allocated by the generic builder and platform core. This file contributes static descriptor metadata only; no persistent storage, firmware writes, or module-global mutable state beyond the descriptor object are used.

Dependencies and integration points: It depends on `pinctrl-sunxi.h`, Linux platform/OF matching, and the DT child binding using `pins`, `function`, and `allwinner,pinmux`. It integrates with GPIO, IRQ, pinmux, and pin configuration paths implemented by the shared sunxi pinctrl core.

Risks: The critical risks are bad bank counts, an incorrect IRQ bank map, or a wrong IRQ mux value, because those errors would create invalid pin numbers or misroute external interrupts. Because functions are DT-supplied, binding drift or missing DT pin groups can silently remove expected mux options. The new register-layout and eleven-bank flags must match the A523 register block exactly.

Test signals: Useful checks include boot probing on an A523 DT, validating all expected pin names PB0..PK23/PK24 boundaries, exercising GPIO input/output, testing external interrupts on each IRQ bank, and confirming voltage bias configuration through boards using multiple IO domains.
