# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_benchmark.c

Purpose: provides a developer benchmark for Radeon buffer-object copy throughput across GTT and VRAM domains using DMA and/or blit copy engines.

Important APIs/functions: public `radeon_benchmark` dispatches benchmark scenarios by test number. `radeon_benchmark_move` allocates, reserves, pins, benchmarks, unpins, and releases source/destination BOs. `radeon_benchmark_do_move` repeatedly submits DMA or blit copies and waits on fences. `radeon_benchmark_log_results` reports throughput. Constants define copy method IDs, 1024 iterations, and a table of common display-mode-sized buffers.

Control flow: each requested test chooses domain pairs and buffer sizes. For each move, the code creates a source BO in the source domain and destination BO in the destination domain, pins both, runs DMA copy if available, runs blit copy if available, waits synchronously after each submitted fence, logs elapsed time in jiffies converted to milliseconds, and cleans up BO reservations/pins/references on all paths.

State and persistence: creates transient GPU buffer objects, fence objects, and reservation use during the benchmark. It does not persist results beyond DRM log output and does not alter long-lived driver state except normal BO/fence accounting and possible GPU engine activity.

Dependencies and integration: uses Radeon TTM BO helpers, GEM memory domain constants, copy engine hooks in `rdev->asic->copy`, fence wait/unref APIs, `jiffies`, and DRM logging. It is typically triggered by driver benchmark/debug paths rather than normal display operation.

Risks: synchronous fence waiting for 1024 iterations can take significant time and load the GPU. Throughput calculation divides by elapsed milliseconds only when nonzero, so very fast runs skip logging instead of reporting infinity. Cleanup reports a generic error based on the last `r` value, which may be overwritten by cleanup reservation attempts. Running on memory-pressure systems can fail BO allocation or pinning.

Test signals: manual benchmark invocation for test numbers 1-8; DRM log throughput lines for DMA and blit paths; error logs for unsupported copy methods or BO move failures; GPU hang/fence timeout monitoring under benchmark load.
