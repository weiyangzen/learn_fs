# sources/distributed-fs/ipfs-kubo/profile/profile.go

Purpose: implements Kubo diagnostic profile collection into a caller-provided zip archive. The public entry point is `WriteProfiles(ctx, archive, opts)`, driven by `Options` and collector constants for goroutine stacks, pprof profiles, version metadata, binary copy, CPU/mutex/block profiles, and runtime trace.

Important APIs and control flow: `profiler.runProfile` validates collector names, filters collectors through `enabledFunc`, starts enabled collectors concurrently, buffers each result, then serializes each buffer into the zip. Sampling collectors wait for `ProfileDuration`; mutex and block collectors temporarily change global runtime profiling settings and restore them with defers.

State and persistence: no long-lived application state, but it reads the current executable, runtime pprof state, and version metadata, and writes zip members. CPU profiling, tracing, mutex fraction, and block profiling are global process resources, so concurrent callers can interfere.

Dependencies and integration: uses Go `runtime/pprof`, `runtime/trace`, `archive/zip`, Kubo version info, and `WriteAllGoroutineStacks`. Integrated with debug/profiling workflows that need a portable bundle.

Risks and test signals: unknown collector names fail early; context cancellation cancels duration-based collectors. Risks include huge binary zip entries, global runtime profile mutation, and duplicate result sends after collector errors. Tests cover enabled/disabled collectors and Windows executable naming.
