# sources/distributed-fs/ceph-client/drivers/hwmon/kbatt.c

## Purpose
`kbatt.c` is an auxiliary-bus hwmon driver for the KEBA battery monitoring controller FPGA IP core. It exposes a single voltage-style minimum alarm indicating whether the monitored battery fails a load test.

## Important APIs, types, and functions
The driver uses the auxiliary bus, KEBA auxiliary device structures from `linux/misc/keba.h`, MMIO helpers, `fsleep()`, mutexes, and the hwmon `with_info` API. `struct kbatt` stores the MMIO base, lock, cached alarm result, and next allowed update time. `kbatt_alarm()` performs the hardware load test and caches the result. `kbatt_read()` returns the alarm value and `kbatt_is_visible()` exposes only `in0_min_alarm`.

## Control flow
Probe obtains the parent-provided I/O resource from `struct keba_batt_auxdev`, maps it with `devm_ioremap_resource()`, initializes the mutex, and registers the hwmon device named `kbatt`. When users read the alarm, `kbatt_alarm()` checks the jiffies throttle; if expired, it writes the battery-test bit, waits 100 ms, reads status, clears the test bit, and delays the next test by up to 10 seconds.

## State and persistence
The driver intentionally caches the alarm result to avoid constantly applying the test load. Hardware control state is restored to load-off after each test. Runtime state is not persistent across driver reloads.

## Dependencies and integration points
It depends on a KEBA parent driver creating auxiliary device `keba.batt` with a valid MMIO resource. It integrates only through hwmon and auxiliary-bus matching.

## Risks
The read path has side effects and can hold the mutex while sleeping for the settle time. If an error or future change skipped the load-off write, the battery could remain under test load. The alarm is stale for up to 10 seconds by design. There is no explicit hardware revision validation in this child driver, so parent resource correctness is critical.

## Test signals
Test auxiliary probe with valid and invalid resources, alarm read when status indicates OK/fail, jiffies throttling, concurrent sysfs reads, load bit clear after reads, and absence of any other exposed hwmon attributes.
