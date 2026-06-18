# subset-b-004015 Research

Grouped research for the listed Ceph-client kernel-source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_core.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_core.c

## Purpose
Implements the core Windfarm framework used by PowerMac thermal-control drivers. It owns the global lists of `wf_control` and `wf_sensor` objects, exposes them as attributes on a synthetic `windfarm` platform device, broadcasts notifier events to platform control-loop clients, and runs the once-per-second `kwindfarm` tick thread.

## Important APIs, Types, And Functions
Exports `wf_register_control()`, `wf_unregister_control()`, `wf_get_control()`, `wf_put_control()`, `wf_register_sensor()`, `wf_unregister_sensor()`, `wf_get_sensor()`, `wf_put_sensor()`, `wf_register_client()`, `wf_unregister_client()`, `wf_set_overtemp()`, and `wf_clear_overtemp()`. Sysfs helpers call each object's ops: controls support `get_value`, `set_value`, `get_min`, and `get_max`; sensors expose fixed-point values with `FIX32TOPRINT`. `wf_thread_func()` emits `WF_EVENT_TICK` once per second and performs critical overtemperature escalation.

## Control Flow
Providers register controls and sensors under `wf_lock`, receive duplicate-name protection, and trigger `WF_EVENT_NEW_CONTROL` or `WF_EVENT_NEW_SENSOR`. Clients register a blocking notifier, immediately receive callbacks for all existing objects, and start the tick thread when the first client appears. The thread calls notifiers without the core mutex only for ticks, matching the locking warning in `windfarm.h`.

## State, Dependencies, And Integration
State is process-global: `wf_controls`, `wf_sensors`, `wf_client_list`, reference counts, overtemperature counters, and `wf_thread`. It depends on krefs, blocking notifiers, kthreads/freezer support, platform devices, sysfs device attributes, module ownership, and `call_usermodehelper("/sbin/critical_overtemp")`. Platform model drivers bind to the `"windfarm"` platform device and use the notifier stream.

## Risks And Test Signals
Lifetime is subtle: sysfs attributes embed in provider-owned objects, and notifier callbacks except ticks run under `wf_lock`, so recursive core calls can deadlock. Overtemperature handling invokes usermode after roughly 10 ticks and powers off after roughly 30 ticks. Test signals include duplicate registration, module get/put balance, sysfs read/write paths, notifier ordering for late clients, tick thread start/stop, freezer behavior, and overtemperature refcount transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_cpufreq_clamp.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_cpufreq_clamp.c

## Purpose
Provides a Windfarm boolean control named `cpufreq-clamp` that forces CPU 0's cpufreq maximum limit down to the hardware minimum during thermal failures and restores it to the maximum when cleared.

## Important APIs, Types, And Functions
The control ops are `clamp_set()`, `clamp_get()`, `clamp_min()`, and `clamp_max()`. `wf_cpufreq_clamp_init()` obtains CPU 0's `cpufreq_policy`, records `cpuinfo.min_freq` and `cpuinfo.max_freq`, installs a `FREQ_QOS_MAX` request, creates a `wf_control`, and registers it. Exit unregisters the Windfarm control and removes the QoS request.

## Control Flow
Thermal clients call `wf_control_set_max()` on this control to clamp, because its max is `1`; they call `wf_control_set_min()` to unclamp. `clamp_set()` chooses `min_freq` for any nonzero value and `max_freq` for zero, updates the global `clamped` flag, and calls `freq_qos_update_request()`.

## State, Dependencies, And Integration
Global state includes `clamped`, `clamp_control`, the `freq_qos_request`, and cached min/max frequency values. It depends on cpufreq, CPU device discovery, Linux frequency QoS, and Windfarm control registration. Platform controllers treat it as optional but use it aggressively on sensor/fan failures and overtemperature.

## Risks And Test Signals
The driver only tracks CPU 0 policy, so correctness depends on platform cpufreq policy topology matching all relevant CPUs. Probe can defer when cpufreq is not ready. Failure paths must remove the QoS request exactly once. Test signals include module load before/after cpufreq, sysfs control writes of `0` and `1`, thermal-client clamp/unclamp transitions, and checking effective cpufreq max constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_cpufreq_clamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_fcu_controls.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_fcu_controls.c

## Purpose
Implements Windfarm fan controls for PowerMac FCU I2C fan controllers. It discovers fan and pump channels from device tree, maps Apple location names to Windfarm control names, exposes RPM and PWM controls, and derives min/max limits from MPU EEPROM data or conservative defaults.

## Important APIs, Types, And Functions
`struct wf_fcu_priv` stores the I2C client, lock, fan list, kref, and RPM shift. `struct wf_fcu_fan` wraps one `wf_control`. Low-level I2C helpers are `wf_fcu_read_reg()` and `wf_fcu_write_reg()`. RPM ops are `wf_fcu_fan_set_rpm()` and `wf_fcu_fan_get_rpm()`; PWM ops are `wf_fcu_fan_set_pwm()` and `wf_fcu_fan_get_pwm()`. Discovery is handled by `wf_fcu_lookup_fans()`, `wf_fcu_default_fans()`, `wf_fcu_add_fan()`, and `wf_fcu_init_chip()`.

## Control Flow
Probe allocates controller state, initializes FCU active masks and the RPM shift, scans child nodes for `fan-rpm-control`, `fan-rpm`, `fan-pwm-control`, or `fan-pwm`, and registers controls. If device-tree discovery fails on PowerMac7,2, a hardcoded fan list is used. Set operations clamp requested values to `fan->min` and `fan->max`, encode RPM or PWM register values, and write the FCU. Get operations check failure and active bitmaps before reading programmed RPM or PWM state.

## State, Dependencies, And Integration
State is per I2C FCU and per registered fan. The private kref keeps controller state alive while controls exist. It depends on I2C master transfers, OF child properties (`location`, `reg`, node type), Windfarm control APIs, and `wf_get_mpu()` for CPU fan and pump limits. PM72 and RM31 model drivers consume the generated controls by stable names such as `cpu-front-fan-0`, `cpu-pump-0`, and `slots-fan`.

## Risks And Test Signals
I2C retry behavior is asymmetric and write operations are not protected by `pv->lock`, unlike reads. Device-tree name translation is fragile and missed names leave models without required controls. Pump min/max EEPROM data is known unreliable and falls back only after sanity checks. Test signals include FCU register read/write errors, inactive/failure bit handling, PowerMac7,2 fallback fan creation, RPM shift detection, duplicate names, and control-loop response to `-EFAULT` fan failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_fcu_controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm75_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm75_sensor.c

## Purpose
Registers LM75 and DS1775 I2C temperature sensors as Windfarm sensors on PowerMac systems, translating Apple device-tree `hwsensor-location` strings into canonical thermal-loop sensor names.

## Important APIs, Types, And Functions
`struct wf_lm75_sensor` stores DS1775 type, lazy initialization state, the I2C client, and embedded `wf_sensor`. `wf_lm75_get()` clears the shutdown bit on first use, waits 200 ms after wake, reads register 0 with SMBus word access, and converts the raw little-endian value into Windfarm 16.16 fixed point. `wf_lm75_probe()` maps locations to names such as `hd-temp`, `incoming-air-temp`, `optical-drive-temp`, `slots-temp`, and CPU inlet temperatures.

## Control Flow
The I2C driver matches `"MAC,lm75"`, `"MAC,ds1775"`, or OF compatibles `"lm75"`/`"ds1775"`. Probe rejects unsupported or unnamed locations, allocates the wrapper, stores client data, and registers the sensor. Remove nulls `lm->i2c` before unregistering so racing reads fail with `-ENODEV`.

## State, Dependencies, And Integration
State is per I2C client and persists until remove/release. It depends on I2C SMBus helpers, OF properties, and Windfarm sensor registration. Platform drivers consume the resulting names for hard-drive, optical-drive, incoming-air, slot, and CPU inlet loops.

## Risks And Test Signals
The DS1775 flag is recorded but not otherwise used. Sensor discovery is only as complete as the hardcoded location string table. The raw conversion assumes the Apple firmware/device endian format expected by this driver. Test signals include first-read initialization, missing location rejection, supported location mapping, remove/read races returning `-ENODEV`, and sysfs fixed-point temperature output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm75_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm87_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm87_sensor.c

## Purpose
Exposes the LM87 internal temperature sensor as a Windfarm sensor for Xserve G5 (`RackMac3,1`) systems, primarily for DIMM and processor-area thermal loops.

## Important APIs, Types, And Functions
`struct wf_lm87_sensor` wraps an I2C client and `wf_sensor`. `wf_lm87_read_reg()` performs register select and byte read with up to ten retries. `wf_lm87_get()` reads `LM87_INT_TEMP` (`0x27`) and returns the integer Celsius value shifted to 16.16 fixed point. `wf_lm87_probe()` scans child nodes named `int-temp`, looks at their `location`, and maps DIMM-related locations to `dimms-temp` and processor-related locations to `between-cpus-temp`.

## Control Flow
Module init refuses non-`RackMac3,1` machines, then registers an I2C driver for `"MAC,lm87cimt"` or OF compatible `"lm87cimt"`. Probe registers only recognized child-location combinations. Remove nulls the client pointer and unregisters the sensor.

## State, Dependencies, And Integration
The driver depends on I2C master send/receive, OF child-node traversal, and Windfarm sensor APIs. RM31 consumes `dimms-temp` to clamp CPU fan output and backside fan minimum; other Xserve loops may use the between-CPU sensor name if present.

## Risks And Test Signals
Only the internal LM87 temperature is exposed, despite the chip supporting more sensors. The retry loop handles transient bus errors but prints a hard error after repeated failures. Recognition depends on location substrings. Test signals include machine-compatible gating, child-node parsing, retry/error behavior, fixed-point conversion, and unregister races returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm87_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_max6690_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_max6690_sensor.c

## Purpose
Registers MAX6690 I2C external-temperature readings as Windfarm sensors for backside, north-bridge, and GPU ambient temperatures used by PowerMac thermal loops.

## Important APIs, Types, And Functions
`struct wf_6690_sensor` stores the I2C client and embedded `wf_sensor`. `wf_max6690_get()` reads `MAX6690_EXTERNAL_TEMP` via SMBus byte access and returns it as 16.16 fixed point. `wf_max6690_probe()` maps `hwsensor-location` values `"BACKSIDE"`/`"SYS CTRLR AMBIENT"` to `backside-temp`, `"NB Ambient"` to `north-bridge-temp`, and `"GPU Ambient"` to `gpu-temp`.

## Control Flow
The module is a standard I2C driver matching `"MAC,max6690"` or OF compatible `"max6690"`. Probe rejects missing or unrecognized location strings, allocates a sensor wrapper, attaches it to client data, and registers it with Windfarm. Remove sets `max->i2c` to NULL and unregisters.

## State, Dependencies, And Integration
State is per I2C client. It depends on SMBus reads, OF properties, and Windfarm sensor registration. PM72, PM81, PM112, PM121, and related model drivers consume the canonical names in backside, north-bridge, and GPU control loops.

## Risks And Test Signals
The chip is assumed firmware-initialized and only its external temperature register is surfaced. Location-string drift causes silent `-ENXIO` probe failure for otherwise working chips. Test signals include supported/unsupported location probes, SMBus read failures, sysfs fixed-point values, and model-loop behavior when `backside-temp`, `north-bridge-temp`, or `gpu-temp` is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_max6690_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_mpu.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_mpu.h

## Purpose
Defines the PowerMac G5 MPU EEPROM calibration layout and provides `wf_get_mpu()` for model drivers that need CPU thermal, fan, pump, and PID calibration data.

## Important APIs, Types, And Functions
`struct mpu_data` describes the 0xa0-byte CPU card calibration blob, including target/max temperatures, max power adjustment, PID gains, diode calibration, heatsink parameters, fan min/max RPMs, pump hints in `processor_part_num`, serial numbers, and checksums. `wf_get_mpu(int cpu)` builds a fixed OF path to `/u3@0,f8000000/i2c@f8001000/cpuid@a0` or `cpuid@a2`, fetches the `cpuid` property, drops the node reference, and returns a pointer to the property data.

## Control Flow
Consumers call `wf_get_mpu()` at model-driver init or fan discovery time. PM72 and RM31 require MPU data before registering their platform drivers, while FCU controls use it opportunistically to refine fan and pump limits.

## State, Dependencies, And Integration
The header has no mutable state. It depends on Open Firmware device-tree APIs and PowerMac-specific immutable device trees. Integration points include `windfarm_fcu_controls.c`, `windfarm_pm72.c`, and `windfarm_rm31.c`.

## Risks And Test Signals
The helper intentionally returns a pointer after `of_node_put()`, relying on non-removable PowerMac OF nodes. It hardcodes U3/I2C paths and unit-address assumptions, so it is not generic across other Apple layouts. Test signals include MPU lookup for CPU 0/1, sane PID history and fan min/max fields, pump fallback behavior when EEPROM values are invalid, and failure paths when MPU data is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_mpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.c

## Purpose
Implements reusable fixed-point PID algorithms for Windfarm thermal control loops: a general single-input PID and a CPU-specific controller that combines power and temperature.

## Important APIs, Types, And Functions
Exports `wf_pid_init()`, `wf_pid_run()`, `wf_cpu_pid_init()`, and `wf_cpu_pid_run()`. The simple PID stores sample/error history, calculates integral and derivative terms over `history_len`, applies gains shifted by 36 bits, optionally adds to the previous target, and clamps to min/max. The CPU PID computes power error against `pmaxadj`, uses the integral term to adjust an effective temperature target, derives temperature change from a two-sample history, applies proportional temperature error, and updates/clamps the output target.

## Control Flow
Model drivers initialize state once when all required sensors and controls are present. Each Windfarm tick passes the latest fixed-point sensor values into the appropriate run function and applies the returned target to one or more fans or pumps.

## State, Dependencies, And Integration
All persistent state lives in caller-owned `wf_pid_state` or `wf_cpu_pid_state` objects. The module depends only on integer arithmetic and exported kernel module symbols. Integration is broad: PM72, PM81, PM91, PM112, PM121, RM31, and ancillary fan loops use these helpers.

## Risks And Test Signals
The functions trust `history_len` to be valid and nonzero; some callers clamp it, others depend on firmware data being sane. Fixed-point scaling and overflow boundaries are critical because gains and history sums use mixed 32/64-bit arithmetic. Test signals include first-sample history initialization, additive versus absolute targets, min/max clamping, large gain behavior, zero/oversized history protection by callers, and CPU PID response to rising temperature with falling or excessive power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.h

## Purpose
Declares Windfarm PID parameter and state structures used by PowerMac thermal model drivers and the PID implementation module.

## Important APIs, Types, And Functions
`struct wf_pid_param` captures simple PID interval, history length, additive mode, derivative/proportional/reset gains, input target, and output min/max. `struct wf_pid_state` stores first-run state, current sample index, current target, sample/error history, and a private copy of parameters. `struct wf_cpu_pid_param` adds CPU-specific `pmaxadj`, `ttarget`, and `tmax`; `struct wf_cpu_pid_state` stores power, error, and two-temperature histories plus `last_delta`. The header declares the four exported init/run functions.

## Control Flow
Callers fill a parameter struct from hardcoded Darwin-derived tables, SMU SDB partitions, or MPU EEPROM fields, then call the init function. Tick handlers call run functions and propagate the resulting target to Windfarm controls.

## State, Dependencies, And Integration
The header depends on kernel integer types through its includers and defines `WF_PID_MAX_HISTORY` and `WF_CPU_PID_MAX_HISTORY` as 32. It is included by all Windfarm model-controller files and by `windfarm_pid.c`.

## Risks And Test Signals
The maximum history constants are compile-time array sizes, but the run functions do not enforce them internally. Firmware-derived history lengths must be clamped by callers. Test signals are compile coverage of each model driver, history length validation, and thermal-loop startup with copied parameter values that remain stable even if the caller's stack struct goes away.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm112.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm112.c

## Purpose
Implements the Windfarm thermal-control client for dual-core desktop PowerMac11,2 G5 systems with SMU and PPC970MP processors. It coordinates per-core CPU fan control, backside/U4, PCI slots, drive bay, overtemperature handling, and optional cpufreq clamping.

## Important APIs, Types, And Functions
Core routines include `create_cpu_loop()`, `cpu_fans_tick()`, `cpu_check_overtemp()`, `backside_fan_tick()`, `slots_fan_tick()`, `drive_bay_fan_tick()`, `set_fail_state()`, and `pm112_tick()`. Discovery callbacks `pm112_new_control()` and `pm112_new_sensor()` bind named Windfarm objects. The platform driver registers a notifier block on the shared `"windfarm"` platform device.

## Control Flow
Init gates on `PowerMac11,2`, counts CPU cores, requests provider modules when built as a module, and registers the platform driver. The notifier accumulates required controls and sensors. Once ready, each tick lazily creates CPU PID state from SMU SAT FVT/PID partitions, then reads every core's `cpu-temp-N` and `cpu-power-N`, chooses the target from the core with greatest thermal delta, limits fan decreases to 20 RPM per tick, scales pump/inlet fan outputs, and runs ancillary loops at their configured intervals.

## State, Dependencies, And Integration
Persistent state includes arrays of per-core sensors, CPU fan controls, CPU PID states, 180-second maximum-temperature history, ancillary PID state, fan scaling, readiness flags, and failure bits. It depends on SMU SAT partitions via `smu_sat_get_sdb_partition()`, Windfarm PID helpers, Windfarm control/sensor reference APIs, OF machine matching, and `machine_power_off()`.

## Risks And Test Signals
The driver assumes exact provider names and can wait forever if a required object never registers. High overtemperature powers off immediately; low overtemperature ramps fans and blocks normal control until cleared. History initialization starts from zero rather than first sample, so early average calculations are conservative in a different way than PM72/RM31. Test signals include missing SAT partitions, per-core sensor failures, fan set failures, pump scale calculations, cpufreq clamp transitions, and overtemperature immediate/average paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm112.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm121.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm121.c

## Purpose
Implements iMac G5 iSight (`PowerMac12,1`) thermal control. It re-creates Darwin-style fan loops for hard drive, optical drive, GPU, north bridge/KODIAK, and CPU fans, including model-specific target corrections and linked fan dependencies.

## Important APIs, Types, And Functions
Important structures include `pm121_correction`, `pm121_connection`, `pm121_sys_param`, `pm121_sys_state`, and `pm121_cpu_state`. `pm121_correct()` applies average-power output-low-bound correction, while `pm121_connect()` applies model-specific linked fan rubber-banding. Loop setup/tick functions are `pm121_create_sys_fans()`, `pm121_sys_fans_tick()`, `pm121_create_cpu_fans()`, and `pm121_cpu_fans_tick()`. `pm121_init_pm()` reads SMU sensor-tree model ID.

## Control Flow
The notifier waits for CPU, drive, optical, incoming-air, north-bridge, GPU, current, voltage, power, and fan controls. On first tick, it creates all system fan loops and the CPU loop. Each tick computes average CPU power from CPU PID history, runs system loops in the order required by linked corrections, runs the CPU loop, handles failure transitions by maxing controls and unclamping on recovery, and uses Windfarm core overtemperature notification with two skipped ticks after a new overtemp.

## State, Dependencies, And Integration
State includes model ID, arrays of controls, individual sensor pointers, per-loop PID states, failure/readjust/skipping flags, overtemp state, average power, and current model connection. It depends on SMU SDB partitions (`SENSORTREE`, `CPUPIDDATA`, `FVT`), Windfarm PID/control APIs, SMU/LM75/MAX6690 provider modules, and cpufreq clamp.

## Risks And Test Signals
`pm121_connection = &pm121_connections[pm121_mach_model - 2]` assumes model IDs 2 or 3; bad or missing SDB data can index incorrectly. `pm121_connect()` appears to read the control's current value rather than the reference control, so linked correction behavior should be audited against intent. Required sensor strictness includes `incoming-air-temp` even though it is marked unused. Test signals include model 2 versus model 3 fan mapping, correction math, CPU PID SDB parsing, overtemp notify/clear, and failure recovery readjust behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm121.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm72.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm72.c

## Purpose
Implements thermal control for AGP PowerMac G5 `PowerMac7,2` and `PowerMac7,3` systems. It uses FCU fan controls, MPU EEPROM calibration, LM75/AD7417/MAX6690 sensors, and optional cpufreq clamp.

## Important APIs, Types, And Functions
Key routines are `read_one_cpu_vals()`, `cpu_setup_pid()`, `cpu_fans_tick_split()`, `cpu_fans_tick_combined()`, `cpu_check_overtemp()`, `backside_setup_pid()`, `backside_fan_tick()`, `drives_setup_pid()`, `drives_fan_tick()`, and `pm72_tick()`. Discovery callbacks bind `cpu-front-fan-N`, `cpu-rear-fan-N`, optional `cpu-pump-N`, `backside-fan`, `slots-fan`, `drive-bay-fan`, `cpufreq-clamp`, and CPU diode/voltage/current sensors.

## Control Flow
Init gates on PowerMac7,2/7,3, counts up to two CPU chips, requires MPU data for each, requests provider modules, and registers the Windfarm client. Once all required objects exist, the first tick initializes CPU PID loops from MPU fields, backside and drive PID loops, and fixes the slot fan to a default PWM. Systems with pumps switch to a combined liquid-cooling algorithm using the max temp/power across CPUs and scaled pump speed; otherwise each CPU is controlled separately with intake fan scaling.

## State, Dependencies, And Integration
State includes per-chip sensor/control arrays, MPU data pointers, CPU PID state, overtemp history, backside/drive PID state, topology flags, and failure bits. It depends on `wf_get_mpu()`, FCU controls, Windfarm PID helpers, OF machine and CPU-node enumeration, and `machine_power_off()`.

## Risks And Test Signals
Provider callbacks store raw pointers without `wf_get_*()` references, unlike newer SMU model drivers; unload races are mostly tolerated by platform assumptions. High overtemp powers off directly, and low overtemp/failure clamps cpufreq and maxes fans. Liquid-cooled pump calculations depend on valid MPU max exhaust RPM and pump controls. Test signals include one-chip/two-chip configurations, pump detection, MPU field sanity, split versus combined CPU control, backside U3 revision parameter selection, drive sensor failure, and cpufreq failure transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm72.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm81.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm81.c

## Purpose
Implements thermal control for first-generation iMac G5 systems (`PowerMac8,1` and `PowerMac8,2`). It controls system, drive-bay, and CPU fans using Darwin-derived PID tables and SMU SDB CPU calibration.

## Important APIs, Types, And Functions
System-loop parameters are represented by `wf_smu_sys_fans_param` and `wf_smu_sys_fans_state`; CPU-loop state by `wf_smu_cpu_fans_state`. Setup/tick functions are `wf_smu_create_sys_fans()`, `wf_smu_sys_fans_tick()`, `wf_smu_create_cpu_fans()`, `wf_smu_cpu_fans_tick()`, and `wf_smu_tick()`. Notifier callbacks `wf_smu_new_control()` and `wf_smu_new_sensor()` bind required Windfarm objects.

## Control Flow
Init reads the SMU sensor-tree model ID and registers only on PowerMac8,1/8,2. The notifier waits for `cpu-fan`, `system-fan`, `cpufreq-clamp`, optionally `drive-bay-fan`, plus `cpu-power`, `cpu-temp`, and `hd-temp`. First tick creates system and CPU loops. System fan ticks every five seconds from hard-drive temperature, scales one output for system fan, optionally drives the hard-drive fan directly, and cross-couples with the CPU target. CPU ticks every second from CPU temp/power and cross-couples with system target.

## State, Dependencies, And Integration
Persistent state includes model ID, sensor/control refs, PID state allocations, failure bits, readjust/skipping flags, and overtemp flag. It depends on Windfarm core and PID helpers, SMU SDB partitions (`SENSORTREE`, `CPUPIDDATA`, `FVT`), SMU/LM75 sensor providers, and cpufreq clamp.

## Risks And Test Signals
Removal uses a one-second delay due to notifier lifetime uncertainty and comments note possible sysfs/provider races. Model tables only cover IDs 2, 3, and 5, while init gates by machine compatible, so odd sensor-tree data can leave loops failed and fans maxed. Test signals include each model table path, missing drive fan on models greater than 3, SDB history clamping, overtemp notify/clear, readjust after failure recovery, and provider module unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm81.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm91.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm91.c

## Purpose
Implements Windfarm thermal control for the single-CPU desktop G5 `PowerMac9,1`. It manages CPU fan group, drive-bay fan, and slots fan using SMU sensors and PID loops.

## Important APIs, Types, And Functions
Important routines are `wf_smu_create_cpu_fans()`, `wf_smu_cpu_fans_tick()`, `wf_smu_create_drive_fans()`, `wf_smu_drive_fans_tick()`, `wf_smu_create_slots_fans()`, `wf_smu_slots_fans_tick()`, and `wf_smu_tick()`. The notifier binds `cpu-rear-fan-0`, `cpu-rear-fan-1` or `cpu-front-fan-0`, `drive-bay-fan`, `slots-fan`, `cpufreq-clamp`, and sensors `cpu-power`, `cpu-temp`, `hd-temp`, and `slots-power`.

## Control Flow
Init registers only on `PowerMac9,1` and requests SMU control/sensor, LM75, and clamp modules. First ready tick initializes drive, slots, and CPU loops. CPU PID uses SMU CPUPIDDATA and FVT partitions. Drive fan uses a five-second PID on hard-drive temperature, with additive mode depending on whether the control is RPM. Slots fan uses a one-second reset-only PID on slots power. Failures cause cpufreq clamp and all fans to max; recovery unclamps and forces readjust.

## State, Dependencies, And Integration
State includes sensor/control references, three allocated PID state objects, failure bits, readjust/skipping flags, and overtemp flag. It integrates with Windfarm notifiers, Windfarm PID helpers, SMU SDB partitions, and provider-created named controls.

## Risks And Test Signals
As with PM81, removal comments acknowledge notifier/sysfs lifetime races. CPU control requires one primary fan and at least one secondary/third fan; missing names prevent startup. Slots overtemp detection is disabled under `#if 0`, so slots power only affects fan speed. Test signals include SMU SDB absence, CPU secondary fan alternatives, drive control additive mode, slots-power sensor errors, cpufreq clamp transitions, and overtemp behavior from CPU or drive loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm91.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_rm31.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_rm31.c

## Purpose
Implements thermal control for Xserve G5 `RackMac3,1`. It handles per-chip triple CPU fans, backside fan, slots fan, DIMM temperature clamping, MPU-calibrated CPU PID loops, and cpufreq failure clamping.

## Important APIs, Types, And Functions
Key functions include `read_one_cpu_vals()`, `cpu_setup_pid()`, `cpu_fans_tick()`, `cpu_check_overtemp()`, `backside_setup_pid()`, `backside_fan_tick()`, `slots_setup_pid()`, `slots_fan_tick()`, and `rm31_tick()`. Discovery callbacks bind `cpu-fan-a/b/c-N`, `backside-fan`, `slots-fan`, `cpufreq-clamp`, CPU diode/voltage/current sensors, `backside-temp`, `slots-temp`, and `dimms-temp`.

## Control Flow
Init gates on `RackMac3,1`, counts up to two CPU chips, requires MPU data, requests FCU and sensor provider modules, and registers the Windfarm client. The first ready tick initializes CPU PID state from MPU EEPROM plus backside, DIMM, and slots PID loops. Each tick runs backside/DIMM and slots loops before CPU loops so DIMM output can clamp CPU fan speed. CPU control reads temp/voltage/current, computes power, checks overtemp, runs per-chip CPU PID, then applies the max of CPU target and DIMM clamp to all three fans for that CPU.

## State, Dependencies, And Integration
State includes two-chip arrays of sensors and fan controls, MPU data, CPU PID state, 180-second CPU temperature history, backside/slots/DIMM PID states, `dimms_output_clamp`, readiness flags, and failure bits. It depends on FCU controls, LM75/LM87/AD7417/MAX6690 sensors, Windfarm PID, OF machine matching, and `machine_power_off()`.

## Risks And Test Signals
The driver stores raw provider pointers without reference acquisition and relies on platform/module assumptions. DIMM PID output is in RPM-like units and is converted into backside percentage minimum as well as CPU clamp, so scaling mistakes affect multiple loops. Test signals include one/two-chip Xserve layouts, LM87 `dimms-temp` discovery, DIMM clamp propagation, slots/backside PID min/max clamping, high-overtemp poweroff, and fan/sensor failure max-fan behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_rm31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_controls.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_controls.c

## Purpose
Registers SMU-managed fan outputs as Windfarm controls for PowerMac systems. It supports RPM and PWM fan nodes under the SMU device tree and sends fan commands through SMU firmware.

## Important APIs, Types, And Functions
`struct smu_fan_control` embeds one `wf_control` and stores fan type, SMU register ID, cached value, and min/max. `smu_set_fan()` sends `SMU_CMD_FAN_COMMAND`, trying the newer command format first and falling back globally to the older bitmap format on failure. `smu_fan_set()`, `smu_fan_get()`, `smu_fan_min()`, and `smu_fan_max()` implement Windfarm control ops. `smu_fan_create()` translates OF `location` names to canonical Windfarm fan names.

## Control Flow
Module init requires `smu_present()`, finds the SMU node, scans `rpm-fans` or compatible `smu-rpm-fans`, then scans `pwm-fans`. Each recognized node with `location`, `min-value`, `max-value`, and `reg` becomes a registered control and is stored on `smu_fans`. Exit unregisters all controls.

## State, Dependencies, And Integration
State is the global `smu_fans` list plus the global fallback flag `smu_supports_new_fans_ops`. It depends on SMU command queue/completion, OF properties, Windfarm control APIs, and provider name stability. PM81, PM91, PM112, and PM121 consume these controls by names such as `cpu-fan`, `system-fan`, `hard-drive-fan`, `optical-drive-fan`, and `cpu-pump-0`.

## Risks And Test Signals
`smu_fan_get()` returns the cached target rather than reading hardware, so sysfs/debug consumers may not see firmware-side changes. The new-command fallback is global after the first failure. Location-name matching is manually curated and case-sensitive. Test signals include old/new SMU command fallback, min/max property absence, unrecognized fan locations, RPM versus PWM control type, command completion status, and exit unregister coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sat.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sat.c

## Purpose
Implements Windfarm sensors for SMU satellite I2C controllers and exports `smu_sat_get_sdb_partition()` so model drivers can fetch per-core calibration partitions from satellite controllers.

## Important APIs, Types, And Functions
`struct wf_sat` stores satellite identity, I2C client, OF node, sensor list, cache, timestamp, kref, and mutex. `struct wf_sat_sensor` maps a cooked sensor index, optional second index for power, shift, and embedded `wf_sensor`. `smu_sat_get_sdb_partition()` selects a partition by ID, reads its length, fetches 4-byte blocks with byte swapping, and returns a newly allocated `smu_sdbp_header` buffer. `wf_sat_sensor_get()` refreshes a 16-byte cache when older than 800 ms and converts voltage/current/temp/power values.

## Control Flow
Probe scans child nodes for cooked sensor registers `0x30..0x37` with `location` strings like `CPU A0 ...`, determines chip/core, registers `cpu-voltage-N`, `cpu-current-N`, and `cpu-temp-N`, then synthesizes `cpu-power-N` when both voltage and current indices exist for a core. Remove unregisters all sensors and releases the satellite.

## State, Dependencies, And Integration
Global `sats[2]` allows platform code such as PM112 to fetch SAT partitions by chip ID. Per-satellite cache avoids excessive I2C traffic. Dependencies include I2C SMBus block/word access, OF properties, Windfarm sensor registration, krefs, and mutexes.

## Risks And Test Signals
The partition reader returns allocated memory that callers must free, and it does not attach discovered partitions to the device tree despite a TODO. Probe assumes at most one CPU chip per SAT and specific `CPU [AB][01]` location strings. Test signals include cache refresh timing, power sensor synthesis, byte-order correctness in partition reads, missing partition handling, two-satellite registration in `sats[]`, and remove-time sensor/kref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sensors.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sensors.c

## Purpose
Registers basic SMU ADC-backed sensors and a derived CPU power sensor as Windfarm sensors. It provides CPU temperature, current, voltage, slots power, and CPU power values using SMU SDB calibration partitions.

## Important APIs, Types, And Functions
`struct smu_ad_sensor` wraps one ADC index and `wf_sensor`. `smu_read_adc()` sends `SMU_CMD_READ_ADC` and expects a two-byte reply. Sensor ops scale ADC readings using SDB calibration: `smu_cputemp_get()`, `smu_cpuamp_get()`, `smu_cpuvolt_get()`, and `smu_slotspow_get()`. `struct smu_cpu_power_sensor` combines voltage and current sensors; `smu_cpu_power_get()` either fakes voltage, multiplies V and I, or applies a quadratic transform from `cpuvcp->power_quads`.

## Control Flow
Init requires `smu_present()`, fetches CPUVCP, CPUDIODE, SLOTSPOW, and debug-switch partitions, finds the SMU `sensors` child, creates recognized ADC sensors by OF type/location, tracks CPU voltage/current sensors, and registers `cpu-power` if both exist. Exit unregisters the derived power sensor first, then all basic ADC sensors.

## State, Dependencies, And Integration
Global pointers cache SDB partition data for calibration. `smu_ads` tracks registered basic sensors, and `smu_cpu_power` tracks the derived one. Dependencies include SMU command queue/completion, SDB partition APIs, OF traversal, Windfarm sensor references, and fixed-point arithmetic. PM81/PM91/PM121 and other SMU model loops consume `cpu-temp`, `cpu-current`, `cpu-voltage`, `cpu-power`, and `slots-power`.

## Risks And Test Signals
Calibration partitions are mandatory for some sensor types; missing partitions cause individual sensor creation to fail. The fake-voltage debug switch and quadratic transform are machine/version dependent. `smu_read_adc()` casts command buffer data to `u16 *`, so reply length and alignment matter. Test signals include SDB partition absence, ADC command status/reply length errors, faked voltage path, quadratic power path, derived sensor reference cleanup, and fixed-point output scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mailbox/Kconfig

## Purpose
Defines the Linux mailbox subsystem configuration menu and individual mailbox controller/test-client options for many SoC families and firmware interfaces.

## Important APIs, Types, And Functions
This is declarative Kconfig. `menuconfig MAILBOX` enables the mailbox framework. Nested symbols include ARM MHU/MHUv2/MHUv3, platform MHU, PL320, PCC, OMAP, Rockchip, Qualcomm, MediaTek, Broadcom, STM32, Tegra, Xilinx, RISC-V SBI MPXY, and many others. Dependencies constrain build visibility by architecture, OF/ACPI, `HAS_IOMEM`, AMBA, SBI, or `COMPILE_TEST`; selected symbols can also select helper infrastructure such as `GENERIC_MSI_IRQ`.

## Control Flow
Kernel configuration tools evaluate dependencies and user choices. If `MAILBOX` is disabled, all nested mailbox controller options are hidden and their Makefile objects are not selected. If enabled, each chosen tristate/bool symbol drives compilation and module availability.

## State, Dependencies, And Integration
The file persists build-time configuration in `.config`, not runtime state. It integrates directly with `drivers/mailbox/Makefile` through matching `CONFIG_*` symbols and indirectly with device-tree or ACPI platform discovery in each driver.

## Risks And Test Signals
Incorrect dependencies can expose drivers on unsupported builds or hide valid compile-test coverage. Help text and module names can drift from Makefile object names. Test signals include `allyesconfig`, architecture-specific defconfigs, `COMPILE_TEST` builds, Kconfig dependency warnings, and checking that every Makefile object has a reachable config symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mailbox/Makefile

## Purpose
Maps mailbox Kconfig symbols to object files for the Linux mailbox framework and controller drivers.

## Important APIs, Types, And Functions
This is a kbuild Makefile. `obj-$(CONFIG_MAILBOX) += mailbox.o` builds the generic framework. Each `CONFIG_*` appends the corresponding controller object, such as `arm_mhu.o arm_mhu_db.o` for `CONFIG_ARM_MHU`, `arm_mhuv2.o` for `CONFIG_ARM_MHU_V2`, `pcc.o` for `CONFIG_PCC`, and SoC-specific mailbox drivers for Qualcomm, MediaTek, Broadcom, Xilinx, RISC-V, and others.

## Control Flow
Kbuild expands `obj-y` and `obj-m` according to the final `.config`. Composite modules are not defined here; each listed source compiles as its own object/module except `CONFIG_ARM_MHU`, which includes both the regular and doorbell ARM MHU implementations under the same symbol.

## State, Dependencies, And Integration
There is no runtime state. The file depends on symbol definitions in `Kconfig` and source filenames in `drivers/mailbox`. It integrates with the kernel build system and module installation.

## Risks And Test Signals
Symbol/object drift is the main risk: missing objects silently omit drivers, and stale objects break builds. The shared `CONFIG_ARM_MHU` entry builds both `arm_mhu.o` and `arm_mhu_db.o`, so both must remain compatible with that Kconfig dependency set. Test signals include `make drivers/mailbox/`, allmodconfig, randconfig, and cross-checking new Kconfig entries against Makefile additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu.c

## Purpose
Implements the original ARM Message Handling Unit mailbox controller driver for AMBA devices with three physical channels: low priority, high priority, and secure.

## Important APIs, Types, And Functions
`struct mhu_link` stores one channel's IRQ and TX/RX register bases. `struct arm_mhu` stores the mapped base, three links, three mailbox channels, and the controller. Mailbox ops are `mhu_send_data()`, `mhu_startup()`, `mhu_shutdown()`, and `mhu_last_tx_done()`. `mhu_rx_interrupt()` reads interrupt status, reports the 32-bit value to the mailbox client, and clears the same bits.

## Control Flow
Probe requires OF compatible `"arm,mhu"`, maps the AMBA resource, assigns each channel an IRQ and register window, configures mailbox polling for TX completion, and registers the controller. Startup clears any pending TX status and requests the channel IRQ. Sending writes the caller-provided `u32` to `INTR_SET`; TX is complete when the peer clears `INTR_STAT`.

## State, Dependencies, And Integration
State is per AMBA device and per channel. The driver depends on AMBA probing, MMIO accessors, interrupts, OF compatible matching, and the generic mailbox controller framework. Clients reference channels from device tree using the standard mailbox binding for this controller.

## Risks And Test Signals
It trusts `data` to point to a `u32`. IRQs are requested per channel on startup with `IRQF_SHARED`, so teardown and duplicate startup paths matter. Secure channel availability is hardware/security-state dependent but still exposed as one of three channels. Test signals include RX interrupt clear behavior, TX polling, absent/invalid IRQs, shared IRQ handling returning `IRQ_NONE` when status is zero, and channel ordering in device-tree clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu_db.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu_db.c

## Purpose
Implements the ARM MHU doorbell variant. It exposes individual doorbell bits within the three physical MHU channels as dynamically allocated mailbox channels.

## Important APIs, Types, And Functions
`struct mhu_db_link` stores physical channel IRQ and TX/RX registers. `struct mhu_db_channel` stores parent controller, physical channel index, and doorbell bit. `mhu_db_mbox_xlate()` translates a two-cell mailbox specifier `(physical-channel, doorbell)` into a free mailbox channel. `mhu_db_send_data()` sets the selected doorbell bit; `mhu_db_last_tx_done()` checks whether it is still set; `mhu_db_mbox_rx_handler()` maps IRQ status bits back to registered channels, calls `mbox_chan_received_data()`, and clears each bit.

## Control Flow
Probe requires `"arm,mhu-doorbell"` and `#mbox-cells = <2>`, maps registers, allocates up to `MHU_CHAN_MAX` channel slots, registers the controller with a custom `of_xlate`, then requests one threaded IRQ per present physical channel. A client request allocates a `mhu_db_channel` in the first free slot; shutdown clears the bit and frees that private data.

## State, Dependencies, And Integration
State includes fixed physical link info and dynamically populated mailbox channel `con_priv` entries. It depends on AMBA, OF mailbox specifiers, devm memory/IRQ management, MMIO register access, and the generic mailbox framework. It builds with `CONFIG_ARM_MHU` alongside the non-doorbell driver.

## Risks And Test Signals
Only twenty logical channels are reserved even though hardware has up to 96 doorbells, trading RAM for capacity. IRQ handler status scanning reports unregistered doorbells as errors and loops until no registered pending channel remains. `devm_kfree()` on shutdown must not conflict with devm cleanup. Test signals include invalid specifier bounds, duplicate doorbell allocation, channel exhaustion, unregistered doorbell IRQs, TX polling, and shutdown/reallocation of the same doorbell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv2.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv2.c

## Purpose
Implements the ARM MHUv2 mailbox controller for AMBA devices. It supports unidirectional sender or receiver frames and two device-tree-described transport protocols: doorbell and data-transfer.

## Important APIs, Types, And Functions
Packed register structs model sender and receiver frames. `struct mhuv2` stores the mailbox controller, mapped frame, frame type, IRQ, hardware window count, architecture minor revision, raw protocol table, and a doorbell pending spinlock. `struct mhuv2_mbox_chan_priv` records protocol ops, channel-window index, doorbell bit, data-transfer window count, and pending state. Protocol ops include doorbell startup/read/send/txdone and data-transfer startup/read/send/txdone. Top-level ops are `mhuv2_sender_*`, `mhuv2_receiver_*`, and `mhuv2_mbox_of_xlate()`.

## Control Flow
Probe maps the AMBA resource, selects TX init for `"arm,mhuv2-tx"` or RX init for `"arm,mhuv2-rx"`, reads implemented window count and architecture minor revision, parses `arm,mhuv2-protocols`, verifies total windows and protocol IDs, allocates mailbox channels, and registers the controller. TX frames request access from the receiver and use interrupts for minor version 1+ if available, otherwise polling. RX frames require an IRQ, mask all windows initially, and unmask per-channel during startup.

## State, Dependencies, And Integration
Runtime state is per controller and per generated mailbox channel. It depends on AMBA IDs for MHUv2 2.0/2.1, OF resource and protocol parsing, MMIO access, threaded IRQs, spinlocks, the mailbox framework, and `linux/mailbox/arm_mhuv2_message.h` for data-transfer payloads. Device-tree clients address channels by window offset and doorbell index.

## Risks And Test Signals
Several busy-wait loops spin until peer state changes (`access_ready`, data-transfer TX completion). Data-transfer requires the first word of each round to be nonzero so the receiver interrupt fires. Doorbell TX completion uses a pending bit under spinlock to distinguish newly completed bits from concurrent sends. `BUG_ON()` is used for impossible states and could hard-stop malformed hardware/logic cases. Test signals include protocol-table validation, channel count math, doorbell exact-channel IRQ decoding, combined interrupt versus status scanning by minor version, short data-transfer masking, TX interrupt fallback to polling, RX on unattached channels, and sender remove clearing `access_request`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv2.c -->
