# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f55.c

## Purpose

`rmi_f55.c` implements RMI4 Function 55 sensor-electrode assignment discovery. It reads RX/TX electrode counts and, when sensor assignment is supported, counts enabled receive/transmit electrodes so other functions can size diagnostic data correctly.

## Important APIs, Types, and Functions

`struct f55_data` stores raw query bytes and raw/configured RX/TX electrode counts. `rmi_f55_detect()` reads F55 query registers, updates `rmi_driver_data->num_rx_electrodes` and `num_tx_electrodes`, and optionally reads control assignment tables. `rmi_f55_probe()` allocates state and runs detection.

## Control Flow

Probe allocates `f55_data`, stores it on the function device, and calls detect. Detect reads three query bytes, records raw RX/TX counts, initializes configured counts, and publishes them to the RMI driver data. If the physical-characteristics byte advertises sensor assignment, it reads F55 Control1 and Control2 assignment arrays, counts entries not equal to `0xff`, and publishes those enabled counts instead.

## State and Persistence Behavior

F55 persists only discovered geometry in its own state and in shared `rmi_driver_data`. It does not modify hardware. The shared counts persist for later consumers such as F54 report sizing.

## Dependencies and Integration Points

The file depends on RMI block reads, RMI function driver data, and the shared `rmi_driver_data` geometry fields. It integrates most directly with F54 diagnostics, which consults shared electrode counts before falling back to F54 query counts.

## Risks and Edge Cases

The code assigns `cfg_num_tx_electrodes` and `drv_data->num_tx_electrodes` from `num_rx_electrodes` in the default path, which appears wrong for asymmetric sensors. Assignment-table read errors are ignored after the query succeeds, leaving default counts. Fixed `u8 buf[256]` assumes electrode counts fit in one byte-sized table.

## Test Signals

Useful checks include symmetric and asymmetric RX/TX devices, assignment-present and assignment-absent devices, assignment tables containing `0xff` holes, control-read failures, and downstream F54 report sizing with and without F55 data.
