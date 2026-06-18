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
