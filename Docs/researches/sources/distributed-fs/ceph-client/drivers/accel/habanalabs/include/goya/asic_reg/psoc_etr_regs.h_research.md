# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_etr_regs.h

Purpose: maps the PSOC Embedded Trace Router/Trace Sink register block used for CoreSight trace capture. It defines 46 addresses for buffer size/status/pointers, trigger/control/mode, buffer watermarks, AXI target address/control, flush/status controls, integration-test registers, lock/access registers, authentication, and component IDs.

Important APIs/types/functions: macro-only `mmPSOC_ETR_*` definitions from `mmPSOC_ETR_RSZ` at `0x2C43004` through `mmPSOC_ETR_COMPID3` at `0x2C43FFC`. High-traffic macros include `mmPSOC_ETR_LAR`, `mmPSOC_ETR_CTL`, `mmPSOC_ETR_FFCR`, `mmPSOC_ETR_STS`, `mmPSOC_ETR_BUFWM`, `mmPSOC_ETR_RSZ`, `mmPSOC_ETR_MODE`, `mmPSOC_ETR_AXICTL`, `mmPSOC_ETR_DBALO`, and `mmPSOC_ETR_DBAHI`.

Control flow: `goya_coresight.c` and equivalent code unlock the ETR via `LAR`, stop/flush using `CTL` and `FFCR`, poll `FFCR`/`STS`, configure trace buffer size/mode/watermark, program AXI attributes and destination base address, then enable capture with `CTL`.

State and persistence: trace sink state persists in ETR hardware and in the configured trace buffer. Read/write pointers and high bits are observed after capture to locate collected trace data.

Dependencies and integration: included by `goya_regs.h`. It integrates with `PSOC_GLOBAL_CONF_TRACE_ADDR` masks for high address bits and with CoreSight helper code that applies unlock constants and timeout polling.

Risks: trace buffer base/size errors can corrupt memory through AXI writes. Flush and stop sequences are timing-sensitive; skipping polls can lose trace data. Access-lock registers must be programmed before protected ETR writes.

Test signals: CoreSight enable/disable tests, trace capture into host memory, FFCR/STS timeout handling, pointer readback, and component ID sanity checks exercise this map.
