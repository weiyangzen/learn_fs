# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/core.c

## Purpose

This file provides the legacy Intel SoC telemetry core API. It is a thin dispatcher from exported telemetry functions to platform-specific operations installed by `pltdrv.c`.

## Important APIs, Types, And Functions

`struct telemetry_core_config` holds current platform config and operation table. Exported APIs include `telemetry_read_events()`, `telemetry_read_eventlog()`, `telemetry_raw_read_eventlog()`, `telemetry_get_trace_verbosity()`, `telemetry_set_trace_verbosity()`, `telemetry_set_pltdata()`, `telemetry_clear_pltdata()`, `telemetry_get_pltdata()`, and `telemetry_get_evtname()`. Default operations return success without data until platform data is installed.

## Control Flow

Module init sets `telm_core_conf.telem_ops` to default no-op operations. The platform driver later calls `telemetry_set_pltdata()` with real operations and event maps. API callers then dispatch into those operations. `telemetry_get_evtname()` selects PSS or IOSS event name arrays from the platform config.

## State And Persistence

Global state is a single platform config pointer and ops pointer. There is no locking in core setters/getters; platform lifetime ordering is expected to prevent races. No persistent state exists.

## Dependencies And Integration Points

It depends on `asm/intel_telemetry.h` for UAPI-like telemetry structs and is consumed by platform, debugfs, and other in-kernel telemetry users.

## Risks

If callers use read APIs before platform data is set, default callbacks return 0, which can look like successful empty reads. There is no refcounting around `plt_config`, so debugfs must not outlive cleared platform data. Event-name access copies pointers from current config without synchronization.

## Test Signals

API calls before and after platform driver load, clear-on-remove behavior, PSS/IOSS event-name retrieval, and debugfs consumer behavior validate the core.
