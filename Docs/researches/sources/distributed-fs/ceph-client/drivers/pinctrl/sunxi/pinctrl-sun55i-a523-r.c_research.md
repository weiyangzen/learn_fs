# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun55i-a523-r.c

## Purpose

This file provides the Allwinner A523 R-PIO controller descriptor using the newer device-tree-table helper rather than a hand-written pin array. It covers PL and PM sleep-domain banks with generated pin descriptors, IRQ bank mapping, IRQ mux values, and IO-bias settings.

## Important APIs, Types, And Functions

Important objects are `a523_r_nr_bank_pins[]`, `a523_r_irq_bank_map[]`, `a523_r_irq_bank_muxes[]`, `a523_r_pinctrl_data`, `a523_r_pinctrl_probe()`, `a523_r_pinctrl_match[]`, and `a523_r_pinctrl_driver`. Probe calls `sunxi_pinctrl_dt_table_init()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT`.

## Control Flow

The built-in platform driver matches `allwinner,sun55i-a523-r-pinctrl`. Probe asks the common DT-table helper to synthesize the pin table from bank sizes `{ 14, 6 }`, IRQ mux values `{ 14, 14 }`, descriptor metadata, and the new register-layout flag. The common core then registers pins and services GPIO, pinmux, pinconf, and IRQ requests.

## State And Persistence

The static arrays describe bank shape and IRQ capabilities. The generated pin table and driver state are owned by the common sunxi core after initialization. Runtime state persists only in R-PIO hardware registers until reset or reconfiguration. IO bias uses `BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Dependencies And Integration Points

The file depends on `pinctrl-sunxi-dt` support through `sunxi_pinctrl_dt_table_init()`, OF platform matching, and the common sunxi core. It integrates PL/PM R-PIO pins starting at `PL_BASE`, two IRQ banks, mux value 14 for IRQ mode, and the new register layout used by newer Allwinner controllers.

## Risks

Because pins are generated, the bank-size and IRQ-mux arrays are the source of truth; a wrong count shifts every generated pin after the error. `a523_r_pinctrl_data` is non-const because the helper populates descriptor fields, so accidental reuse across multiple instances would need review. The new register layout, `PL_BASE`, IO-bias variant, and IRQ mux value must all match A523 R-PIO hardware.

## Test Signals

Validate A523 R-PIO probe, generated debugfs pin names for PL0-PL13 and PM0-PM5, GPIO tests across both banks, IRQ tests using mux value 14, IO-bias readback, and suspend/wake paths that rely on R-PIO pins.
