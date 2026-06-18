# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu-core.c

## Purpose
`coresight-ctcu-core.c` implements the Qualcomm CoreSight TMC Control Unit helper. It programs per-ETR ATID filter registers so a TMC ETR sink accepts or rejects trace streams based on CoreSight trace ID bits.

## Important APIs, Types, And Functions
Platform configuration is described by `ctcu_etr_config` arrays; this file provides SA8775P offsets for two ETR ports. `ctcu_program_atid_register()` unlocks the device, sets or clears one trace-ID bit in an ATID register, and relocks it. `__ctcu_set_etr_traceid()` validates port configuration and trace ID, applies a per-port/per-trace-ID reference count, and only touches hardware on 0-to-1 or 1-to-0 transitions. `ctcu_get_active_port()` maps the active sink connection to a CTCU destination port. `ctcu_enable()` and `ctcu_disable()` are CoreSight helper callbacks.

## Control Flow
Probe allocates a CoreSight helper device name, loads CoreSight platform data, maps registers, enables clocks, copies SoC match data into `drvdata->atid_offset[]`, initializes the spinlock, and registers a helper subtype `CORESIGHT_DEV_SUBTYPE_HELPER_CTCU`. Runtime PM is enabled by the platform wrapper. During path enable, CoreSight helper handling calls `ctcu_enable()`, which extracts the path sink and assigned trace ID, finds the sink's active CTCU port, and sets the corresponding ATID bit. Disable clears the bit when the reference count drops to zero.

## State And Persistence
`struct ctcu_drvdata` stores MMIO base, APB clock, CoreSight device, spinlock, ATID offsets, and `traceid_refcnt[ETR_MAX_NUM][CORESIGHT_TRACE_ID_RES_TOP]`. Reference counts preserve correct behavior when multiple paths use the same trace ID and sink port. Hardware ATID state persists while the device is powered and is reconstructed by future enables.

## Dependencies And Integration Points
The driver depends on CoreSight helper topology, trace ID allocation, runtime PM, OF match data, clocks, and CoreSight lock macros. It integrates specifically with ETR sinks connected through firmware-described CTCU ports.

## Risks
`__ctcu_set_etr_traceid()` uses an unsigned 8-bit refcount; an unmatched disable can underflow before assignment and may program hardware incorrectly if call ordering is broken. The bounds check uses `reg_offset - atid_offset > CTCU_ATID_REG_SIZE`; exact end-offset semantics should be reviewed because the register window is four 32-bit registers. The `port_num` field from match data is not used when copying offsets; current code assumes array index equals port number.

## Test Signals
Tests should validate OF probe on SA8775P, helper association with ETR paths, trace ID bit set/clear for each ETR port, repeated enable/disable refcounting, invalid trace ID rejection, invalid port rejection, and runtime PM suspend/resume. Hardware trace should confirm ETR filtering changes when ATID bits are toggled.
