<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c

## Purpose

Provides cpufreq support for AMD K6-2+/K6-3+ PowerNow processors by changing the CPU multiplier through the K6 EPMR-enabled PowerNow I/O port.

## APIs, Types, And Functions

`powernow_k6_driver` supplies `init`, `exit`, `target_index`, `get`, and generic table verification. `clock_ratio` maps cpufreq indices to multiplier values, while `index_to_register` and `register_to_index` translate between table order and BVC register encoding. Module parameters `max_multiplier` and `bus_frequency` override frequency detection.

## Control Flow

`powernow_k6_init()` verifies AMD family/model support, reserves the fake PowerNow I/O window, and registers cpufreq. `powernow_k6_cpu_init()` only accepts CPU0, infers max multiplier from `cpu_khz` against `usual_frequency_table` unless overridden, computes FSB in 10 kHz units, fills the frequency table, and sets latency. Targeting validates the requested multiplier and calls `powernow_k6_set_cpu_multiplier()`.

## State And Persistence

Global `busfreq` and `max_multiplier` persist derived platform state. The hardware multiplier is read and changed by enabling `MSR_K6_EPMR`, accessing `POWERNOW_IOPORT + 0x8`, then disabling the port. During writes, interrupts are disabled, CR0 cache disable is set, and `wbinvd()` flushes cache while the processor may stop responding to inquiry cycles.

## Dependencies And Integration Points

Depends on x86 CPU matching, MSR access, I/O port reservation, `cpu_khz`, and the cpufreq frequency table core. It integrates only as a uniprocessor CPU0 driver.

## Risks And Test Signals

The driver is hazardous by design: wrong FSB or max multiplier parameters can produce invalid rates, and multiplier writes disable cache and interrupts. CPU exit attempts to restore the maximum multiplier. Test signals are successful I/O region reservation, correct multiplier readback from `get`, table invalidation above max multiplier, and stable transitions across every valid table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c -->
