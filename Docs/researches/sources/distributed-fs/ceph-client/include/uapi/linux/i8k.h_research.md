<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h

## Purpose
`i8k.h` defines the userspace ABI for the Dell laptop SMM BIOS access driver historically exposed through `/proc/i8k` and ioctl commands.

## Important APIs, types, and functions
Constants include `I8K_PROC`, `I8K_PROC_FMT`, ioctls `I8K_BIOS_VERSION`, `I8K_MACHINE_ID`, `I8K_POWER_STATUS`, `I8K_FN_STATUS`, `I8K_GET_TEMP`, `I8K_GET_SPEED`, `I8K_GET_FAN`, and `I8K_SET_FAN`, fan IDs (`I8K_FAN_LEFT`, `I8K_FAN_RIGHT`), fan levels (`OFF`, `LOW`, `HIGH`, `TURBO`, `AUTO`, `MAX`), volume/Fn status bits, and AC/battery values.

## Control flow
User tools query BIOS and machine identity, read power/Fn/temp/fan state, and optionally set fan speed by issuing ioctls or reading the proc file. The kernel driver translates these calls into SMM BIOS operations.

## State and persistence behavior
Temperature, fan RPM, power, and Fn status are sampled live state. Fan mode changes persist in firmware/platform control until changed by the driver, BIOS, or thermal policy.

## Dependencies and integration points
It integrates with Dell SMM BIOS calls, the i8k driver, procfs compatibility, hwmon/thermal userspace, and fan-control tools.

## Risks and test signals
Risks include broken ioctl sizes noted in comments, machine-specific SMM behavior, unsafe manual fan control, treating `TURBO` and `AUTO` as distinct on all machines, and non-Dell platform probing. Test signals include supported-model detection, read-only telemetry checks, fan set/get round trips under thermal guardrails, proc output format validation, and invalid fan/value rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h -->
