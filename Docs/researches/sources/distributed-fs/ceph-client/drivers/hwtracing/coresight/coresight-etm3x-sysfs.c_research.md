# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-sysfs.c

## Purpose

This file defines the ETM3x/PTM sysfs interface. It exposes discovered hardware capabilities, editable trace configuration fields, selected live hardware status, trace ID metadata, and a small management register group for CoreSight ETM3x devices.

## Important APIs, Types, and Attributes

Read-only capability attributes include `nr_addr_cmp`, `nr_cntr`, `nr_ctxid_cmp`, `cpu`, and `traceid`. Live/status attributes include `etmsr`, `cntr_val`, and `seq_curr_state`. `reset` clears `struct etm_config`, restores defaults, marks address comparators unused, and releases the sysfs trace ID. Other attributes edit mode, trigger/enable events, FIFO level, address comparators, counters, sequencer events, context IDs, sync frequency, and timestamp events. `coresight_etm_groups[]` exports the main and `mgmt` groups.

## Control Flow

Most store handlers parse hexadecimal input, validate it against discovered capability counts or masks, and update the in-memory `struct etm_config`. Index attributes are protected by `drvdata->spinlock` because subsequent accesses dereference the selected index across multiple array fields. Address range setup requires an even comparator index and uses adjacent comparator slots. Mode changes may call `etm_config_trace_mode()` to install kernel/user exclusion ranges.

## State and Persistence

Sysfs writes persist only in `drvdata->config` until the next sysfs enable programs hardware. Some state is refreshed on disable by the ETM3x core, notably counter and sequencer state. Context ID settings are rejected outside the initial PID namespace. Trace ID persists across sysfs disable and is released by `reset`.

## Dependencies and Integration Points

The file depends on `coresight-etm.h`, `coresight-priv.h`, PM runtime, PID namespace helpers, and the ETM3x core's exported default/trace-ID functions. The exported attribute groups are consumed during CoreSight source registration.

## Risks and Test Signals

Many attributes directly edit low-level register images, so invalid combinations can still be created if they pass local bounds checks. Address comparator type state prevents reusing a comparator for incompatible modes without reset. Test sysfs capability values, reset, unsupported mode rejection, address validation, context ID namespace rejection, live vs cached reads, and management register reads.
