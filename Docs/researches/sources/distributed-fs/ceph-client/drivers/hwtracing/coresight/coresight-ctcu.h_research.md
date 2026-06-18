# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu.h

## Purpose
`coresight-ctcu.h` defines the private data structures for the Qualcomm CTCU helper driver and the maximum number of ETR ports it supports.

## Important APIs, Types, And Functions
`ETR_MAX_NUM` caps a single CTCU at two ETR devices. `struct ctcu_etr_config` describes the ATID0 register offset and connected CTCU port number for one ETR. `struct ctcu_config` groups SoC-specific ETR configurations. `struct ctcu_drvdata` holds MMIO base, APB clock, device/CoreSight handles, spinlock, ATID offsets, and per-port/per-trace-ID reference counts.

## Control Flow
The header has no runtime control flow. The CTCU core file uses these structures during probe, helper enable, and helper disable.

## State And Persistence
The critical state is `traceid_refcnt`, sized by `CORESIGHT_TRACE_ID_RES_TOP`, which mirrors the hardware ATID filter bits and prevents premature clearing when more than one path uses the same trace ID on the same ETR.

## Dependencies And Integration Points
The header includes `coresight-trace-id.h` for trace ID capacity. It is private to the CTCU implementation and its SoC match data.

## Risks
The hard-coded `ETR_MAX_NUM` must match all supported SoCs. If future hardware has more than two ETRs, both arrays and probe validation must be updated. The `u8` refcount constrains maximum simultaneous users per trace ID.

## Test Signals
Compile and probe tests should verify the array sizes, SoC config validation, and trace ID reference-count indexing. Future SoC additions should include tests for nontrivial port numbering.
