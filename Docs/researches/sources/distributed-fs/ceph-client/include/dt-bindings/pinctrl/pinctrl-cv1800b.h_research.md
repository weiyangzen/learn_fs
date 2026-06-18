<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h

## Purpose

`pinctrl-cv1800b.h` defines Sophgo CV1800B package pin identifiers for device-tree pinmux entries. It is generated from vendor pinout data and is paired with the shared CV18xx `PINMUX()` encoding.

## Important APIs, Types, and Functions

The file includes `dt-bindings/pinctrl/pinctrl-cv18xx.h` and exports 49 pin constants such as `PIN_SD0_*`, `PIN_UART0_*`, `PIN_SPINOR_*`, `PIN_IIC0_*`, `PIN_SD1_*`, `PIN_ETH_*`, `PIN_MIPIRX*`, and audio/ADC/power pins. Values are numeric package pin IDs with gaps, ranging from `PIN_AUD_AOUTR` at 1 to `PIN_AUD_AINL_MIC` at 67.

## Control Flow

No executable flow is present. DTS uses `PINMUX(PIN_*, mux)` or `PINMUX2()` from `pinctrl-cv18xx.h`; this file supplies the first `pin` argument.

## State and Persistence Behavior

The header is stateless. Pin selections are stored in DTS/DTB and are applied by the CV18xx/Sophgo pinctrl driver during boot or state changes.

## Dependencies and Integration Points

The required dependency is `pinctrl-cv18xx.h`, which defines the 32-bit packed encoding. Integration points are CV1800B DTS files, the Sophgo pinctrl binding, and the pinctrl driver's package-specific pin tables.

## Risks and Edge Cases

The numeric IDs are package-specific and sparse. Reusing CV1812H, SG2000, or SG2002 pin names without checking numeric values can select the wrong physical ball. Because the header only names pins, it does not constrain mux values; unsupported mux selections can still compile if written with `PINMUX()`.

## Test Signals

Use DTS compilation, `dtbs_check`, static comparison against vendor pinout tables, and runtime pinctrl debugfs. Hardware smoke tests should cover SD0/SD1, SPI NOR, UART0, I2C0, Ethernet, MIPI RX, ADC, and audio pins present on the target board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h -->
