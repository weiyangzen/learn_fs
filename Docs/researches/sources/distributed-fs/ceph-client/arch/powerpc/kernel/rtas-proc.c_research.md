# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-proc.c

## Purpose
`rtas-proc.c` creates legacy `/proc/powerpc/rtas/*` interfaces for pSeries RTAS services: progress display, clock, scheduled power-on, sensors, tone frequency/volume, and user RTAS RMO buffer discovery.

## Important APIs, Types, And Functions
Important structures are `struct individual_sensor` and `struct rtas_sensors`. `proc_rtas_init()` creates proc entries. Write/show handlers include `ppc_rtas_poweron_write/show`, `ppc_rtas_progress_write/show`, `ppc_rtas_clock_write/show`, `ppc_rtas_tone_freq_write/show`, `ppc_rtas_tone_volume_write/show`, and `ppc_rtas_rmo_buf_show`. Sensor helpers include `ppc_rtas_find_all_sensors()`, `ppc_rtas_process_error()`, `ppc_rtas_process_sensor()`, `check_location_string()`, and `get_location_code()`.

## Control Flow
Initialization only proceeds on `machine_is(pseries)` and when an `rtas` device node exists. User writes are parsed as decimal numbers through `parse_number()` or copied into `progress_led`; handlers call the matching RTAS token via `rtas_call()` or `rtas_progress()`. Sensor display reads the `rtas-sensors` property, then for each token/quantity calls `get-sensor-state`, formats known token classes, appends RTAS condition text, and decodes optional location-code strings from `ibm,sensor-XXXX` properties.

## State And Persistence
Global state includes cached `rtas_node`, the last requested `power_on_time`, last `progress_led` string, and tone frequency/volume values. Firmware state changes persist outside the kernel for clock, power-on time, indicators, and progress display.

## Dependencies And Integration Points
The file depends on procfs, seq_file, uaccess, OF property APIs, RTAS token lookup/calls, pSeries machine detection, RTC conversion helpers, and `rtas_rmo_buf` exported by RTAS core. It exposes a userspace ABI under `/proc`.

## Risks
The sensor array is fixed at `MAX_SENSORS` but `ppc_rtas_find_all_sensors()` assigns `sensors.quant = len / 8` without an explicit cap before filling, so malformed firmware with too many sensors would be dangerous. Proc writes are not serialized around global variables. The interfaces are legacy and thinly validate semantic ranges except tone volume clamping. User access to the RMO buffer is explicitly not arbitrated by the kernel.

## Test Signals
Tests should verify proc entry creation only on pSeries with RTAS, clock/power-on writes with valid and invalid decimal input, progress string truncation, tone frequency/volume writes, sensor formatting for known and unknown tokens, location-code parsing, behavior when `rtas-sensors` is absent, and RMO buffer output formatting.
