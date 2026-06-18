<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h

## Purpose

`pinctrl-sg2002.h` defines Sophgo SG2002 package pin identifiers for device-tree pinmux entries using the shared CV18xx encoding.

## Important APIs, Types, and Functions

The file includes `pinctrl-cv18xx.h` and exports 65 numeric pin constants. Named pins cover audio input/output, SD0/SD1, speaker enable, UART0, eMMC, JTAG CPU, IIC0, auxiliary and GPIO_ZQ pins, power sequencing/reset/wakeup/button pins, ADC, USB VBUS, Ethernet differential pins, GPIO_RTX, MIPI RX lanes, and MIPI TX lanes. Numeric values range from 2 through 88 with gaps.

## Control Flow

There is no runtime flow. DTS entries use these constants as the `pin` argument to `PINMUX()` or `PINMUX2()`, and the pinctrl driver interprets the packed value when applying states.

## State and Persistence Behavior

The header stores no mutable state. The only persistence is the selected constants in source and compiled device trees. Hardware pin state is owned by the pinctrl subsystem at runtime.

## Dependencies and Integration Points

The direct dependency is the shared CV18xx packing header. Integration points are SG2002 DTS files, binding schemas, and the Sophgo pinctrl driver's SG2002 pin tables.

## Risks and Edge Cases

SG2002 uses simple numeric IDs rather than `PINPOS()` row/column values, so copy/paste from SG2000/CV1812H can be wrong even when signal names match. The file does not restrict mux IDs; an unsupported mux value can be packed and compiled. Sparse numbering means range-only validation is insufficient.

## Test Signals

Tests should include DTS compilation, `dtbs_check`, static comparison against vendor pinout definitions, pinctrl debugfs review, and hardware smoke tests for SD/eMMC, UART0, IIC0, Ethernet, USB VBUS, MIPI, ADC, audio, and power pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h -->
