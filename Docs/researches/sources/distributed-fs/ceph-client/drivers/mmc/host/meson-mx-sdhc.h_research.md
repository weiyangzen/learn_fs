# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc.h

## Purpose

`meson-mx-sdhc.h` is the shared register-definition header for the Meson MX SDHC host driver and its embedded clock-controller helper. It centralizes offsets, bitfields, and the clock registration prototype used by `meson-mx-sdhc-mmc.c` and `meson-mx-sdhc-clkc.c`.

## Important APIs, Types, And Functions

- Register offsets cover command argument/send/control/status/clock/address/PDMA/misc/data/interrupt/reset/enhancement/phase registers from `MESON_SDHC_ARGU` through `MESON_SDHC_CLK2`.
- Bitfield macros use `BIT()` and `GENMASK()` for SEND command index/response/data flags, CTRL data type/DDR/pack length/timeouts/endian/IRQ mode, STAT FIFO counts and line state, CLKC divider/power bits, PDMA mode/burst/FIFO thresholds/manual flush, MISC CRC patterns/manual stop, ICTL/ISTA interrupt bits, SRST reset bits, ENHC SoC-specific enhancements, and CLK2 phase fields.
- `struct clk_bulk_data` is forward-declared to avoid including the full clock header in users.
- `meson_mx_sdhc_register_clkc()` is declared as the clock-controller registration function.

## Control Flow And State

There is no executable logic in this header. It defines the hardware state layout that the SDHC host driver mutates during probe, request start, IRQ handling, tuning, FIFO flush, reset, and clock programming. The paired C files rely on these definitions for source-tree-aligned hardware access.

## Dependencies And Integration Points

The header depends on `linux/bitfield.h` for bitfield helpers. It integrates the Meson MX SDHC MMC host and clock-controller helper by sharing the `MESON_SDHC_CLKC` layout and the `meson_mx_sdhc_register_clkc()` declaration.

## Risks And Edge Cases

- Some register bits are SoC-specific but share offsets, especially ENHC fields for Meson6 versus Meson8m2. Callers must use the right platform hook.
- ICTL and ISTA definitions mirror each other; using the wrong register for enable versus status/ack would break IRQ handling.
- Manual FIFO flush and manual stop fields are used for hardware workarounds in the driver and are easy to regress if renamed or altered.

## Test Signals

Signals are indirect: successful compilation of both companion files, correct clock gate/divider register programming, expected interrupt enable/status masks, FIFO flush behavior, manual stop behavior, and tuning phase writes through `MESON_SDHC_CLK2`.
