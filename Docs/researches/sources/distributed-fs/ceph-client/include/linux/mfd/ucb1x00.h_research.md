# sources/distributed-fs/ceph-client/include/linux/mfd/ucb1x00.h

## Purpose
`ucb1x00.h` defines the MFD interface for Philips/NXP UCB1x00 mixed-signal chips attached through MCP/SIB. It covers GPIO, interrupt, audio/telecom, touchscreen, ADC, ID, mode registers, child-driver registration, clock helpers, raw register access, GPIO access, and ADC control.

## Important APIs, Types, and Functions
Register constants include IO data/dir, interrupt rising/falling/status/clear, telecom/audio controls, touchscreen control, ADC control/data, ID, and mode. `struct ucb1x00` stores MCP link, IRQ state, ADC mutex, IO lock/cache, ID, GPIO chip, device, child device lists, and wake/mask state. `struct ucb1x00_driver` provides add/remove/suspend/resume callbacks for child clients. Inline helpers wrap MCP clock enable/disable, clock rate, register read/write, and audio/telecom divisors. Exported APIs register/unregister child drivers, set/read GPIOs, and enable/read/disable ADC.

## Control Flow
The parent MCP driver enables the SIB clock before register access. Child drivers register through the UCB bus list, receive `ucb1x00_dev`, and call GPIO/ADC helpers. ADC reads are serialized by `adc_mutex`; IO direction/output updates are cached and protected by `io_lock`; IRQ enables are tracked separately for rising and falling edges.

## State and Persistence Behavior
Hardware state includes GPIO direction/data, interrupt masks/status, audio/telecom mode, touchscreen bias/mode, ADC conversion state, and mode bits. Software caches IO direction/output, ADC control, IRQ masks/wake state, chip ID, and child driver/device lists.

## Dependencies and Integration Points
The header depends on MCP, device model, GPIO, GPIO driver API, mutexes, spinlocks, and list management. It integrates with touchscreen, ADC, GPIO, audio/telecom, wakeup, and legacy SA-11x0-style MCP infrastructure.

## Risks and Test Signals
Risks include register access without enabling the MCP clock, ADC/GPIO races if locks are bypassed, child driver list lifetime bugs, 16-bit mask misuse, and wake IRQ state mismatches. Test signals are MCP enable/disable balance tests, GPIO direction/value tests, ADC conversion valid-bit polling, touchscreen IRQ tests, child add/remove lifecycle tests, and suspend/resume reset callback coverage.
