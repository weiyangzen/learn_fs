<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h

## Purpose
Provides devicetree reset IDs for Sophgo CV18xx/SG200x-style reset controller consumers.

## Important APIs, Types, And Functions
Exports `RST_*` numeric constants for DDR, codecs, VIP/TPU, USB, Ethernet, NAND/eMMC/SD, SDMA, I2S, UART, I2C, PWM, SPI, GPIO, efuse, watchdogs, timers, audio, camera, Ethernet PHY, and CPU/core auto-clear reset lines.

## Control Flow
No executable control flow. DTS files include the header and pass these constants in reset phandles to reset-controller providers.

## State And Persistence
The numeric IDs are persistent ABI between devicetree sources and the reset controller binding/driver.

## Dependencies And Integration Points
Depends on DTS include preprocessing and matching Sophgo reset-controller hardware definitions.

## Risks And Edge Cases
Renumbering constants breaks existing DTS reset references. Gaps are intentional hardware numbering and should not be compacted.

## Test Signals
Signals are dtc preprocessing success, reset-controller binding checks, and device probe logs showing resets deasserting expected hardware blocks.

Source read size: 98 lines, 2347 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h -->
