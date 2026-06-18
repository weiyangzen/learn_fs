# sources/distributed-fs/ceph-client/tools/perf/util/sideband_evlist.c

`sideband_evlist.c` manages a side-band perf event list and polling thread. It is used to collect auxiliary events while another perf workflow runs, delivering each side-band event to a callback associated with its evsel.

`evlist__add_sb_event()` ensures `sample_id_all` is enabled on the supplied attribute, creates a new evsel at the current evlist index, stores the side-band callback and opaque data in `evsel->side_band`, and appends it to the evlist. `evlist__set_cb()` applies one callback/data pair to all evsels and configures `sample_id_all`, watermark mode, and wakeup watermark for low-latency side-band delivery.

`evlist__start_sb_thread()` prepares and starts collection. It creates maps for the target, configures sample id positions when multiple events exist, opens each evsel on the requested CPUs/threads, mmaps the evlist, enables all counters, clears `evlist->thread.done`, and starts `perf_evlist__poll_thread()` with pthreads. On any setup failure it deletes the evlist and returns `-1`; a null evlist is treated as success/no-op.

The polling thread calls `unshare(CLONE_FS)` first so later namespace transitions with `setns(2)` are not blocked by a shared filesystem context. It then loops until drained: while not draining it polls with a 1000 ms timeout, iterates every mmap, initializes reading, consumes all available events, maps each event back to an evsel through `evlist__event2evsel()`, calls `evsel->side_band.cb(event, data)` when available, logs a warning for unmapped events, consumes the mmap record, and marks data seen. Once `evlist->thread.done` is set, it stops polling and exits after a pass with no remaining data.

`evlist__stop_sb_thread()` sets the done flag, joins the thread, and deletes the evlist. Ownership therefore transfers to the start/stop helpers: failure and normal stop both free the evlist, so callers must not use it afterward.

State is stored in the evlist, evsels, mmap buffers, and `evlist->thread` fields. There is no disk persistence. Runtime side effects include perf_event opens, mmap rings, pthread creation, and `CLONE_FS` unsharing in the polling thread.

Dependencies include perf evlist/evsel/mmap APIs, perf API probing for sample identifier support, Linux perf_event ABI, pthreads, scheduler namespace flags, and debug logging. Integration points include `perf record` or other tools that need side-band data such as namespaces, build IDs, or metadata while primary recording continues.

Risks include deleting the evlist internally on start failure, unsynchronized access to `evlist->thread.done` from another thread, ignoring `unshare(CLONE_FS)` failures, callback execution on the polling thread without isolation from slow or reentrant callbacks, possible missed warning context for unknown events, and ownership surprises because stop always deletes the evlist.

Test signals should include single and multiple side-band events, callback invocation and data pointer preservation, sample-id-all enforcement, startup failure paths for map/open/mmap/enable/thread-create failures, clean draining after setting done, callback behavior under bursts of mmap data, and namespace workloads that require `setns()` after thread creation.
