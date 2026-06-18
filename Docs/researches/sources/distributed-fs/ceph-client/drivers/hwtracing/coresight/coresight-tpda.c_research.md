# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.c

## Purpose

`coresight-tpda.c` implements the Qualcomm Trace, Profiling and Diagnostic Aggregator as a CoreSight link merger. It aggregates TPDM sources, programs per-port element sizes, packetization controls, synchronization counts, flush requests, and a shared system ATID.

## Important APIs, Types, and Functions

Core functions include `tpda_get_element_size`, `tpda_enable_pre_port`, `tpda_enable_port`, `tpda_enable`, `tpda_disable`, and `tpda_trace_id`. Sysfs handlers manage cross-trigger booleans, `global_flush_req`, `syncr_mode`, `syncr_count`, and `port_flush_req`. `tpda_init_default_data` allocates the shared ATID and defaults FREQ timestamping on. `tpda_probe/remove` register the AMBA CoreSight link.

## Control Flow

On enable, the driver locks `spinlock`, programs global TPDA control only for the first active port, then enables the requested input port. Per-port setup walks incoming CoreSight connections, follows filter sources and recursive links, finds exactly one TPDM behind the port, reads `qcom,dsb-element-bits` and/or `qcom,cmb-element-bits`, encodes element size into `TPDA_Pn_CR`, and sets the port enable bit. Disable clears the per-port enable bit when that input's destination refcount reaches zero and decrements the aggregate refcount.

## State and Persistence Behavior

`tpda_drvdata` persists MMIO, CoreSight device, ATID, element-size scratch fields, cross-trigger settings, CMB channel mode, and SYNCR settings. Sysfs stores update shadow fields before the next enable, while flush show/store accesses live registers and requires the device to be enabled. ATID persists from probe to remove.

## Dependencies and Integration Points

The file depends on CoreSight connection topology, TPDM drvdata and helper predicates from `coresight-tpdm.h`, trace ID allocation, AMBA probing, DT firmware properties, and CoreSight lock/unlock access. It is tightly coupled to TPDM element-size properties and path topology.

## Risks and Edge Cases

The recursive element-size search rejects multiple TPDMs on one TPDA port with `-EEXIST`, and warns if no TPDM property is found. Flush sysfs operations fail when disabled and can only set, not clear, request bits. Settings are shadowed without checking whether hardware is currently enabled, so changes may not take effect until the next first-port enable.

## Test Signals

Exercise topology walks with direct TPDM, filtered source, recursive link, missing source, missing element properties, and multiple TPDMs. Verify sysfs validation, enabled-only flush operations, per-port refcount behavior, ATID release, and register programming for 8/32/64-bit CMB/DSB element sizes.
