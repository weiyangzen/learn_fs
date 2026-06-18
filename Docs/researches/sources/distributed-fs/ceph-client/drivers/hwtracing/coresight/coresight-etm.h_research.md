# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm.h

## Purpose

This header is the ETM3x/PTM private interface. It defines ETMv3/PTM register offsets, bit definitions, mode flags, event encodings, configuration state, driver state, register access helpers, and exported functions used by the ETM3x core and sysfs files.

## Important APIs, Types, and Constants

- Register macros cover ETM trace, management, comparator, counter, sequencer, context ID, sync, timestamp, trace ID, power, and OS lock registers.
- Bit macros such as `ETMCR_ETM_PRG`, `ETMCR_ETM_EN`, `ETMCR_CYC_ACC`, `ETMCR_TIMESTAMP_EN`, `ETMTECR1_INC_EXC`, `ETMTECR1_START_STOP`, and `ETMCCER_RETSTACK` compose hardware programming.
- Mode flags `ETM_MODE_*` describe sysfs/perf requested behavior.
- `struct etm_config` is the ETM3x in-memory register image for trace control, address comparators, counters, sequencer transitions, context ID comparators, sync frequency, and timestamp event.
- `struct etm_drvdata` stores per-device hardware and runtime state.
- `etm_writel()` and `etm_readl()` abstract register access through CP14 or memory-mapped IO.

## Control Flow and Integration

The ETM3x core fills `struct etm_drvdata` during AMBA probe and capability discovery, initializes `struct etm_config`, and writes config fields to hardware during enable. The ETM3x sysfs file presents controlled accessors for the fields in `struct etm_config`; perf parsing also writes into the same config before hardware programming.

## State and Persistence

`struct etm_config` is the persistent software copy of user or perf configuration between runs. Disable paths read back sequencer and counter state into this structure. `traceid` is stored in `struct etm_drvdata` and released only in specific sysfs reset or teardown paths.

## Dependencies, Risks, and Test Signals

The header depends on CoreSight private APIs, Linux spinlocks, clocks, and ARM local/CP14 helpers. Register offsets and bit encodings are hardware ABI and must remain exact. Tests should cover sysfs register values, perf and sysfs enable programming, CP14 and MMIO variants, counter/sequencer readback, and trace mode exclusion programming.
