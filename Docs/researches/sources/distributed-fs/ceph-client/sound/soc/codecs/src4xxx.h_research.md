<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h

## Purpose
This header contains the SRC4xxx register addresses, bit masks, register-address helper macros, read-only register definitions, and the shared probe/regmap declarations used by bus glue and the core driver.

## Important APIs, Types, And Definitions
It declares `src4xxx_probe(struct device *dev, struct regmap *regmap, void (*switch_mode)(struct device *dev))` and `extern const struct regmap_config src4xxx_regmap_config`. Register definitions cover reset/power, port A/B format and clock controls, transmitter controls, SRC/DIT IRQ fields, receiver controls and PLL, GPIO, SRC controls, page select, status/subcode/preamble, and I/O ratio registers. `SRC4XXX_BUS_FMT(id)` and `SRC4XXX_BUS_CLK(id)` compute per-port register addresses.

## Control Flow
No executable flow is defined. The core driver uses these symbols to set DAI format, clock dividers, power bits, DIR reference clocks, DAPM mux selectors, and regmap access metadata.

## State And Persistence
No state is allocated. The definitions govern how `src4xxx.c` stores cached defaults and which registers are treated as volatile.

## Dependencies And Integration Points
The declarations require `struct device` and `struct regmap` declarations from included kernel headers in users. The header is shared by `src4xxx.c` and `src4xxx-i2c.c`.

## Risks And Edge Cases
Incorrect register constants or bit masks can silently misroute the SRC/DIR/DIT datapaths. The public probe signature includes an unused `switch_mode` parameter, so future callers may assume a behavior not currently implemented.

## Test Signals
Compile coverage from core and I2C files, DAI format programming, power/reset writes, PLL register writes, and regmap volatile/default tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h -->
