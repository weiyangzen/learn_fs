# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.c

## Purpose
`timerlat.c` provides shared timerlat command behavior: applying timerlat-specific tracefs/BPF configuration, enabling trace instances and auto-analysis, handling DMA latency and CPU idle-state controls, cleanup, and command dispatch between top and hist modes.

## Important APIs, Types, and Functions
Key functions are `timerlat_apply_config()`, `timerlat_enable()`, `timerlat_analyze()`, `timerlat_free()`, and `timerlat_main()`. Static `dma_latency_fd` holds the `/dev/cpu_dma_latency` handle. The file uses `timerlat_params`, `timerlat_bpf_*()` APIs, osnoise setters for timerlat period and print stack, timerlat auto-analysis functions, and utility functions for CPU idle-state control.

## Control Flow
`timerlat_apply_config()` selects tracing mode: `RTLA_NO_BPF=1` forces tracefs mode, missing timerlat sample event disables BPF, otherwise it tries `timerlat_bpf_init()` and falls back on failure. It rejects BPF action programs in tracefs-only mode, loads action programs when requested, sets timerlat period and print-stack depth, auto-selects user workload when the kernel exposes `timerlat_fd`, otherwise selects kernel workload, then delegates common config. `timerlat_enable()` applies DMA latency and idle-state settings, creates and configures the auto-analysis trace instance unless disabled, performs warmup, starts record/AA/primary tracing or attaches BPF, and configures stop thresholds for non-BPF modes. Cleanup restores resources and destroys BPF/AA state.

## State and Persistence
The file can change `/dev/cpu_dma_latency`, CPU idle-state disable settings, tracefs timerlat/osnoise knobs, BPF maps/program attachments, and auxiliary trace instances. Cleanup closes/restores these resources.

## Dependencies and Integration Points
It integrates with `osnoise.c` context management, `common.c` run loop, timerlat top/hist ops, BPF skeleton userspace, timerlat auto-analysis, cpupower support, and timerlat userspace workload detection.

## Risks and Edge Cases
The BPF fallback path is intentionally permissive except when a BPF action was explicitly requested. Idle-state control requires libcpupower support and successful per-CPU save/restore. If `timerlat_enable()` fails after partially creating AA or changing DMA/idle settings, cleanup must still run through `run_tool()` paths. In BPF mode, stop handling differs from tracefs/mixed mode and depends on ring-buffer notifications.

## Test Signals
Test with `RTLA_NO_BPF=1`, missing BPF support, active BPF support, BPF action program loading, userspace and kernel workload modes, DMA latency, deepest idle state, warmup, AA disabled/enabled, threshold stops, and cleanup after early failures.
