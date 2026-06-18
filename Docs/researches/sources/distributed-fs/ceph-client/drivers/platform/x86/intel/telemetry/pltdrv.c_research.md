# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/pltdrv.c

## Purpose

This platform driver implements the hardware-specific legacy telemetry backend for Apollo Lake/Goldmont and Gemini Lake/Goldmont Plus. It configures default PSS and IOSS telemetry events through P-unit and SCU IPC and reads accumulated samples from SSRAM MMIO regions.

## Important APIs, Types, And Functions

Important objects are the default event maps, `telem_apl_config`, `telem_glk_config`, `telemetry_cpu_ids[]`, and platform ops `telm_pltops`. Setup functions include `telemetry_setup()`, `telemetry_setup_evtconfig()`, `telemetry_setup_iossevtconfig()`, and `telemetry_setup_pssevtconfig()`. Read functions include `telem_evtlog_read()`, `telemetry_plt_raw_read_eventlog()`, and `telemetry_plt_read_eventlog()`. Trace controls are `telemetry_plt_get_trace_verbosity()` and `telemetry_plt_set_trace_verbosity()`.

## Control Flow

Probe matches CPU model, selects platform config, obtains PMC parent data, maps PSS and IOSS SSRAM resources, obtains the SCU IPC device, initializes locks, queries telemetry capacity from IOSS and PSS firmware, programs default event maps with reset action, and installs platform ops into the telemetry core. Event setup disables telemetry, optionally clears or appends events, programs event IDs, then enables periodic SRAM tracing with the configured sample period. Reads use a timestamp-stability loop around SSRAM data to avoid torn samples.

## State And Persistence

Platform state is stored in the selected static `telemetry_plt_config`: event maps, event counts, periods, MMIO regmaps, IPC device, PMC pointer, locks, and `telem_in_use`. Firmware telemetry configuration persists in hardware until reset or reconfiguration; software state is volatile.

## Dependencies And Integration Points

The driver depends on P-unit IPC, SCU IPC, PMC BXT, platform MMIO resources, CPU matching, and telemetry core exported functions. Debugfs consumes the installed platform config and ops.

## Risks

Telemetry setup is all-or-nothing and depends on both IOSS and PSS firmware reporting at least 28 SRAM events/registers. `TELEM_MIN_PERIOD` and `TELEM_MAX_PERIOD` store masked rather than shifted values, so consumers must understand the encoding. Updating telemetry is rejected while `telem_in_use` is set. The timestamp loop returns `-EBUSY` if firmware updates too long. Event-map name strings are only initialized for defaults; update-added events can have IDs without meaningful names.

## Test Signals

Probe on supported CPUs, resource mapping, SCU/P-unit IPC command success, default PSS/IOSS event programming, stable SSRAM reads, trace verbosity get/set, telemetry core ops installation/clear, capacity failure behavior, and debugfs output using the configured event maps are key signals.
