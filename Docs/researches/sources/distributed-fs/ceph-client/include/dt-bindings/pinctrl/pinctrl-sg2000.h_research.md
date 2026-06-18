<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h

## Purpose

`pinctrl-sg2000.h` defines Sophgo SG2000 package pin identifiers for use with the shared CV18xx pinmux encoding. It maps named board-visible pins to row/column-derived integer IDs.

## Important APIs, Types, and Functions

The header includes `pinctrl-cv18xx.h`, defines the same `PINPOS(row, col)` helper used by CV1812H, and exports 111 package pin constants. Pins cover MIPI TX/RX, VIVO data, USB, Ethernet, camera controls, audio, SD0/SD1, UART0/2, JTAG, power sequencing, eMMC, IIC/I2C, clock, reset, GPIO_ZQ, and crystal input.

## Control Flow

No executable logic exists. `PINPOS()` produces a package pin ID at preprocessing time, and DTS code usually feeds that value into `PINMUX()` or `PINMUX2()`.

## State and Persistence Behavior

The header is stateless. Selected pinmux entries persist in DTB files and become hardware state when the Sophgo pinctrl driver applies them.

## Dependencies and Integration Points

The direct dependency is `pinctrl-cv18xx.h`. Integration points are SG2000 DTS files, the Sophgo binding, and driver tables that decode row/column pin IDs. The file matches `pinctrl-cv1812h.h` closely, suggesting shared package layout or compatible pin naming.

## Risks and Edge Cases

The row/column formula accepts invalid-looking inputs at preprocessing time if they are syntactically valid character constants and integers. Similar pin names across SG2000 and CV1812H can hide SoC-specific mux availability differences even when package pin IDs match. The header does not validate mux values.

## Test Signals

Run DTS compilation and `dtbs_check`, compare generated pin IDs with SG2000 package documentation, inspect pinctrl debugfs on boot, and test board peripherals using SD/eMMC, MIPI, Ethernet, USB, UART/I2C, camera/VIVO, audio, and power-control pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h -->
