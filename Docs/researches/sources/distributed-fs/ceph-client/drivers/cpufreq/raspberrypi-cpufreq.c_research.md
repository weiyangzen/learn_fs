<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c

## Purpose

Creates runtime OPPs for Raspberry Pi CPUs from firmware-backed clock min/max rates and delegates actual scaling to `cpufreq-dt`.

## APIs, Types, And Functions

The platform driver implements `raspberrypi_cpufreq_probe()` and `raspberrypi_cpufreq_remove()`. It uses `RASPBERRYPI_FREQ_INTERVAL` as the 100 MHz step when creating OPPs.

## Control Flow

Probe gets CPU0, obtains its clock, asks the clock provider for rounded minimum and maximum rates, creates zero-voltage OPPs every 100 MHz between them, and registers a `cpufreq-dt` platform device. On failure or remove it removes all dynamic OPPs and unregisters the delegated platform device.

## State And Persistence

The only driver-owned state is the global `cpufreq_dt` platform-device pointer and dynamic OPPs on CPU0. Persistent frequency behavior is owned by Raspberry Pi firmware/clock driver and `cpufreq-dt`.

## Dependencies And Integration Points

Depends on `clk-raspberrypi` availability, CPU0 device lookup, OPP core dynamic tables, and generic `cpufreq-dt`.

## Risks And Test Signals

The OPP list assumes 100 MHz granularity between rounded min and max; unusual firmware ranges could miss valid rates or include unsupported ones if rounding semantics change. Test signals include CPU0 clock probe deferral, dynamic OPP count, `cpufreq-dt` registration, and available frequencies matching firmware limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c -->
