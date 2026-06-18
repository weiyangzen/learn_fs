# sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.h

## Purpose
`tmon.h` defines the shared constants, structs, globals, and function prototypes used across the TMON thermal monitor. It is the contract between the sysfs backend, main loop, ncurses UI, and PID controller.

## Important APIs, Types, and Functions
Key limits include `MAX_NR_TZONE`, `MAX_NR_CDEV`, `MAX_NR_TRIP`, display sizing constants, thermal bounds, `THERMAL_SYSFS`, `CDEV`, `TZONE`, and log path `TMON_LOG_FILE`. Data types include `struct thermal_data_record`, `struct cdev_info`, `enum trip_type`, `struct trip_point`, `struct tz_info`, `struct tmon_platform_data`, `struct pid_params`, and small enums for cooling-device and thermal-zone categories. The header declares global runtime state (`ticktime`, `time_elapsed`, `target_temp_user`, `ctrl_cdev`, `ptdata`, `p_param`, `trec`, `no_control`) and public functions for controller, TUI, sysfs probing/sampling, and cleanup.

## Control Flow and Integration
The header itself contains no control flow, but it shapes interactions: `tmon.c` initializes and loops, `sysfs.c` fills `ptdata` and `trec`, `tui.c` reads those objects to draw windows and can write sysfs state, and the controller reads `p_param`/thermal records while writing cooling state.

## State and Persistence
All externally declared globals are process-local, but several represent persisted or externalized state: `tmon_log` points to `/var/tmp/tmon.log`, `ptdata` mirrors sysfs discovery, and control functions write back into sysfs.

## Dependencies and Integration Points
The header depends on `sys/time.h`, `pthread.h`, and `FILE` from standard headers included by consumers. Its constants assume Linux thermal sysfs naming and ncurses display layout.

## Risks and Edge Cases
Hard-coded array sizes and display dimensions can truncate or misrepresent systems with many thermal zones, many cooling devices, long type names, or large instance gaps. The fixed `thermal_data_record` design is simple but tightly couples sampling capacity to `MAX_NR_TZONE`. The header exposes many mutable globals, making thread-safety dependent on caller discipline rather than type-level enforcement.

## Test Signals
Build coverage should include all C files that include this header. Runtime tests should stress maximum zones/cooling devices, long names, and controller/UI behavior when no cooling device is in control.
