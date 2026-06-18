# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/trace.h

## Purpose
`trace.h` defines ftrace tracepoints for Tegra VDE register access and H.264 reference-table programming.

## Important APIs, Types, and Functions
The `register_access` event class backs `vde_writel` and `vde_readl`, recording hardware block name, offset, and value. `vde_setup_iram_entry` records IRAM reference-list entries and auxiliary addresses. `vde_ref_l0` and `vde_ref_l1` record reference-list ordering details. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` enable tracepoint generation from `vde.c`.

## Control Flow
`vde.c` defines `CREATE_TRACE_POINTS` and includes this header so the tracepoints are instantiated once. Register wrapper functions call `trace_vde_writel()` and `trace_vde_readl()`, while `h264.c` calls IRAM/reference tracepoints during hardware context setup.

## State and Persistence
Tracepoints do not hold persistent driver state. When enabled, they emit runtime events into the kernel tracing buffers.

## Dependencies and Integration Points
The file depends on Linux tracepoint infrastructure and `vde.h` for `struct tegra_vde` and register base naming. It integrates with ftrace/perf debugging workflows.

## Risks and Edge Cases
The include path is relative to the kernel trace build expectations and must match the source location. `tegra_vde_reg_base_name()` must remain available for trace fast assignment. Trace payloads expose register values and frame numbers useful for debugging but should not be assumed stable ABI.

## Test Signals
Enable Tegra VDE trace events under tracefs during decode, confirm read/write events name SXE/BSEV/MBE/etc. correctly, verify IRAM entry traces match DPB setup, and build with tracing enabled and disabled.
