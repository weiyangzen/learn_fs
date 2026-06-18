<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config

## Purpose
This config file records kernel options needed for GPIO selftests.

## Important APIs, Types, And Functions
It requires `CONFIG_GPIOLIB=y`, `CONFIG_GPIO_CDEV=y`, `CONFIG_GPIO_MOCKUP=m`, `CONFIG_GPIO_SIM=m`, and `CONFIG_GPIO_AGGREGATOR=m`.

## Control Flow
It is consumed by kselftest prerequisite reporting; scripts still do runtime `modprobe` and mount checks.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
It maps to modules and APIs used by the GPIO test scripts and helper binaries.

## Risks
Even with these options, debugfs/configfs mount availability and permissions can still cause skips.

## Test Signals
Kernels matching this config should allow the scripts to load required modules and create simulated GPIO devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/config -->
