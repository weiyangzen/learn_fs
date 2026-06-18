# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-thermal-data.c

## Purpose
`dra752-thermal-data.c` instantiates the static TI bandgap configuration for DRA752, covering five sensors and the ADC-to-temperature conversion table.

## Important APIs, Types, and Functions
It defines `temp_sensor_registers` for core, IVA, MPU, DSPEVE, and GPU; `temp_sensor_data` thresholds/clock limits for each; the `dra752_adc_to_temp` table; and exported `const struct ti_bandgap_data dra752_data`.

## Control Flow
No functions execute here. At probe, `ti-bandgap.c` selects `dra752_data` through OF match, iterates the five sensors, checks efuses, programs alert thresholds, exposes thermal zones, and uses this file's conversion table when reading temperatures.

## State and Persistence Behavior
All objects are static configuration. Runtime state is created in `ti_bandgap` and per-zone thermal data, not in this file.

## Dependencies and Integration Points
It depends on `ti-thermal.h`, `ti-bandgap.h`, and `dra752-bandgap.h`. The CPU sensor registers cpufreq cooling callbacks; all domains use DRA752 PCB gradient constants.

## Risks and Edge Cases
The shared conversion table and `ERRATA_814` feature mean read correctness depends on the triple-read workaround in `ti-bandgap.c`. Register maps span two control/status regions; wrong domain mapping could silently report or alert on the wrong block.

## Test Signals
DRA752 build/probe tests, five thermal zone registrations, CPU cooling registration for MPU, ADC table bounds tests, alert IRQ tests for each status block, and errata read-path coverage.
