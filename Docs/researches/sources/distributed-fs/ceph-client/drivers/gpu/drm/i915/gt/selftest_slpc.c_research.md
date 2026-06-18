# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_slpc.c Research

Purpose: this live suite validates GuC SLPC frequency control: min/max frequency requests, RP0 grant behavior, power scaling, and multi-tile interaction when several GTs exercise SLPC concurrently.

Important APIs/types/functions: helpers `slpc_set_min_freq()`, `slpc_set_max_freq()`, `slpc_set_freq()`, and `slpc_restore_freq()` wrap GuC SLPC H2G calls and delay for completion. `vary_min_freq()`, `vary_max_freq()`, `max_granted_freq()`, and `slpc_power()` perform assertions. `run_test()` is the shared engine/GT harness. Entrypoint `intel_slpc_live_selftests()` runs vary max/min, max granted, power, and tile interaction tests.

Control flow: `run_test()` skips non-SLPC platforms and fused min/max frequencies, initializes a spinner, records original SLPC min/max, forces min to RPn, disables efficient-frequency bias, takes GT PM, and iterates store-dword-capable engines. For each engine it starts a spinner on the kernel context, runs the selected frequency/power assertion, checks actual frequency rises above min for non-power tests, ends the spinner, and restores heartbeats. It then restores original min/max and efficient-frequency behavior. Tile interaction starts one kthread worker per GT and runs `run_test(..., TILE_INTERACTION)` in parallel.

State and persistence: the file changes GuC SLPC min/max frequency limits, ignore-efficient-frequency mode, GT PM wakerefs, engine heartbeat state, and spinner activity. It restores frequency bounds and efficient-frequency mode through `slpc_restore_freq()`, flushes GEM tests, releases PM, and waits for idle.

Dependencies/integration: it depends on GuC SLPC APIs, RPS actual/punit frequency reads, perf-limit registers, librapl, engine spinners, GT iteration across tiles, and kthread workers. Media GT/video engine frequency differences are explicitly skipped for some max-grant checks.

Risks and test signals: risks include H2G latency, pcode throttling, media-engine RP0 differences, RAPL noise, and restoration failure if an early setup path returns before cleanup. Pass signals are SW request bounded by min/max plus request unit tolerance, actual frequency exceeding min under load, RP0 granted or explained by perf-limit reasons, lower-frequency power reduction, and no parallel tile worker errors.
