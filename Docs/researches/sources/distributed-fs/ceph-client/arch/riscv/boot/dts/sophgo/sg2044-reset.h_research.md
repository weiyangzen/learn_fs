<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h

## Purpose
Provides devicetree reset IDs for the Sophgo SG2044 platform.

## Important APIs, Types, And Functions
Exports `RST_*` constants for AP system/core, interrupt/debug blocks, DMA, efuse, RTC/timer/watchdog, I2C/GPIO/PWM/SPI/UART, Ethernet/eMMC/SD, mailbox, C2C/CXP, DDR lanes, BAR/K2K, chiplet/cluster reset groups, TPSYS, SPACC/PKA/security engine, and interrupt controllers.

## Control Flow
There is no runtime flow. DTS files use these integer definitions as reset specifier cells.

## State And Persistence
The values are hardware/binding ABI and persist across kernel versions once consumed by devicetree.

## Dependencies And Integration Points
Integrated with SG2044 devicetree files and the corresponding reset-controller binding/driver.

## Risks And Edge Cases
Incorrect IDs can hold critical interconnect, memory, or security blocks in reset or reset the wrong block. Header guard comment naming is slightly inconsistent but harmless.

## Test Signals
Signals are dtc include success, schema validation for reset consumers, and board boot/probe behavior for reset-controlled peripherals.

Source read size: 128 lines, 3301 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h -->
