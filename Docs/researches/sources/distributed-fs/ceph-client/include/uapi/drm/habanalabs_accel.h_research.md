# sources/distributed-fs/ceph-client/include/uapi/drm/habanalabs_accel.h

## Purpose

`habanalabs_accel.h` defines the DRM accelerator UAPI for Intel/Habana Labs AI accelerators including Goya, Gaudi, Gaudi2, and later devices. It exposes queue/engine identifiers, device information and telemetry, command-buffer lifecycle, command submission, wait and interrupt APIs, device/host memory mapping, DMA-BUF export, timestamp pools, debug/profile configuration, security attestation, and event/error reporting.

## Important APIs, Types, And Constants

The header enumerates queue IDs and engine IDs for supported ASIC generations and defines device resource constants such as SRAM reservations, sync-object/monitor bases, and timestamp pool limits. `HL_INFO_*` operations cover hardware IP info, events, DRAM usage, idle/busy engines, device status/utilization, clocks, reset counts, time sync, CS/PCI counters, throttling, sync managers, energy/power, open stats, DRAM row repair, timeout/RAZWI/page-fault/error records, user mappings, firmware requests, eventfd registration, security attestation, and device signing.

Command buffers use `HL_CB_OP_CREATE`, `DESTROY`, and `INFO` through `hl_cb_in/out` and `union hl_cb_args`. Command submissions use `hl_cs_chunk`, `hl_cs_in/out`, and `union hl_cs_args`, with flags for restore, signal/wait/collective waits, timestamps, staged submission, custom timeout, skip reset, encapsulated signals, signal reservation, engine-core commands, PCI write flush, and engines commands. Waits use `hl_wait_cs_in/out` for sequence waits, multi-CS waits, interrupts, kernel CQ waits, timestamp registration, and status flags. Memory uses `HL_MEM_OP_ALLOC/FREE/MAP/UNMAP/MAP_BLOCK/EXPORT_DMABUF_FD/TS_ALLOC`. Debug/profile configuration uses ETR/ETF/STM/FUNNEL/BMON/SPMU/timestamp/debug mode structs. Concrete ioctls are `DRM_IOCTL_HL_INFO`, `HL_CB`, `HL_CS`, `HL_WAIT_CS`, `HL_MEMORY`, and `HL_DEBUG`.

## Control Flow

Userspace typically queries hardware info and limits, allocates or maps memory, creates command buffers or references user command buffers, submits restore/execution chunks through `HL_CS`, and waits for completion via `HL_WAIT_CS`, eventfd, interrupts, multi-CS waits, or timestamp buffers. Memory can be device DRAM, pinned host memory mapped into device VA, hardware block mappings, DMA-BUF exports, or timestamp pools. Debug flow requires entering exclusive debug mode before configuring trace/profile blocks.

## State And Persistence

The driver maintains per-file/context state for command buffers, command submissions, sequence numbers, signal reservations, memory mappings, timestamp pools, eventfd registrations, debug ownership, and open stats. Device state includes firmware status, clocks, reset counters, DRAM usage, error history, row repair state, and security material. Memory and timestamp allocations persist until explicit free/unmap or FD/context close. Several event queries may succeed with timestamp zero when no new event exists.

## Dependencies And Integration Points

The header includes `<drm/drm.h>` and relies on kernel UAPI bit/size helpers. Runtime integration depends on the Habana Labs DRM accel driver, device firmware/CPUCP, MMU, queues, sync manager, dma-buf, eventfd, interrupts, debug/profile hardware, monitoring tools, profilers, and AI runtime libraries.

## Risks

Queue and engine IDs are ABI tokens and must not be renumbered. CS sequence completion is not simple global ordering; sequence N completing does not necessarily imply N-1 completed. Older-generation internal jobs can continue after external queue completion. Union fields depend heavily on op/flag validation. Host memory mapping pins pages and hint addresses may be ignored. DMA-BUF export address semantics differ for Gaudi1 versus later ASICs. Debug mode is exclusive and can block other users. Error queries with timestamp zero must be treated as no-event.

## Test Signals

Tests should cover UAPI layout on 32/64-bit, info query bounds, hardware IP info per ASIC, eventfd register/unregister, CB create/map/info/destroy and size rejection, CS restore/execution/staged/signal/wait/collective/engine-command paths, wait statuses for completed/busy/timed-out/aborted/multi-CS/interrupt modes, memory alloc/free/map/unmap/map-block/export/timestamp allocation, hint address behavior, DMA-BUF export/import, debug-mode exclusivity, trace configuration, reset/error event reporting, security attestation sizes, and negative tests for invalid queues, stale handles, bad flags, and reset races.
