<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h

## Purpose
Defines the OpenRISC kernel serial baud base for early 8250 console code. The generic header assumes a fixed UART input clock, while OpenRISC derives it from the current CPU clock so early console output is timed correctly.

## Important APIs, Types, And Functions
The only exported interface is `BASE_BAUD`, computed as `cpuinfo_or1k[smp_processor_id()].clock_frequency / 16`. It includes `asm/cpuinfo.h` and is visible only under `__KERNEL__`.

## Control Flow
There is no function flow. Consumers expand the macro during serial setup, after CPU clock frequency has been populated from device tree setup.

## State And Persistence
No state is stored here. It depends on the per-CPU `cpuinfo_or1k` array, so baud behavior changes with the recorded CPU clock.

## Dependencies And Integration Points
Integrates with early 8250 serial console and OpenRISC CPU discovery. It assumes `smp_processor_id()` is valid for the calling context.

## Risks
If `clock_frequency` is unset or wrong, early console output uses the wrong divisor. SMP users must not evaluate the macro before per-CPU CPU info is initialized.

## Test Signals
Boot logs on 8250 early console at the expected baud rate; device-tree CPU `clock-frequency` changes should produce matching serial divisor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h -->
