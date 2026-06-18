# Group Research: group_237_bcachefs_tools_sources_cow_pools_bcachefs_tools_linux_rhashtable_c_s_db1d12646062

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/bcachefs-tools`.

This grouped report covers Linux-kernel compatibility shims, hashing/sorting/unicode/zstd helpers, packaging CI automation, and RAID parity/recovery support files. Every listed file was read in full.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/rhashtable.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/rhashtable.c

## Purpose
Userspace copy/adaptation of Linux's resizable concurrent hash table implementation. It provides the core `rhashtable` and `rhltable` behavior needed by bcachefs-tools code that expects kernel hash-table APIs.

## Key Responsibilities
- Allocates normal or nested bucket tables depending on allocation size and GFP context.
- Supports RCU-style readers and asynchronous rehashing via `work_struct`.
- Grows on high load, optionally shrinks, and handles nested table conversion.
- Implements slow-path insertion, duplicate detection, rhlist collision lists, and iterator/walker APIs.
- Frees hash tables safely after canceling resize work.

## Important APIs
- `rhashtable_init()`, `rhltable_init()`
- `rhashtable_insert_slow()`
- `rhashtable_walk_enter()`, `rhashtable_walk_start_check()`, `rhashtable_walk_next()`, `rhashtable_walk_peek()`, `rhashtable_walk_stop()`, `rhashtable_walk_exit()`
- `rhashtable_free_and_destroy()`, `rhashtable_destroy()`
- `rht_bucket_nested()`, `rht_bucket_nested_insert()`

## Implementation Notes
- Uses `future_tbl` to attach a new table while readers and mutations continue across old/new tables.
- `rht_deferred_worker()` performs grow/shrink/rehash work under `ht->mutex`.
- Insertions that hit excessive chain elasticity return `-EAGAIN` and trigger rehash.
- Iterator state tracks bucket slot, skip count, and rhlist sub-node, and rewinds with `-EAGAIN` on resize.
- Nested tables are allocated in page-sized chunks to avoid very large contiguous bucket arrays.

## Dependencies
Includes kernel-compat headers for atomics, RCU, workqueues, jhash, random, error helpers, slab/vmalloc, and `linux/rhashtable.h`.

## Risks / Porting Notes
- Correctness relies on the local RCU/workqueue/bit-lock compatibility layer behaving closely enough to Linux.
- Nested-table allocation uses `GFP_ATOMIC` and `cmpxchg`; userspace portability depends on matching shim definitions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/rhashtable.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/sched.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/sched.c

## Purpose
Userspace scheduler/task shim for kernel-style blocking and wakeup primitives.

## Key Responsibilities
- Defines thread-local `current`.
- Joins and frees task structs in `__put_task_struct()`.
- Implements `wake_up_process()` using futex wake.
- Implements `schedule()` by waiting on the current task state with futex wait.
- Implements `schedule_timeout()` using a stack timer to wake the current task.
- Initializes a main thread `task_struct` in a constructor.
- Opens `/dev/urandom` when `SYS_getrandom` is unavailable.

## Dependencies
Uses pthread task state indirectly through `task_struct`, userspace RCU futex support, `linux/timer.h`, futex syscalls, and jiffies.

## Integration Notes
This file is foundational for semaphores, waitqueues, workqueues, kthreads, timers, and shrinkers in the bcachefs-tools kernel-compat layer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/semaphore.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/semaphore.c

## Purpose
Kernel-style counting semaphore implementation adapted for userspace compatibility.

## Key Responsibilities
- Implements `down()`, `down_trylock()`, `down_timeout()`, and `up()`.
- Uses `sem->lock`, `sem->count`, and `sem->wait_list`.
- Sleeps contended waiters via `schedule_timeout()`.
- Wakes the first waiter in `__up()` with `wake_up_process()`.

## Implementation Notes
- `down_trylock()` follows Linux semaphore convention: returns `0` on success, `1` on failure.
- Timeout waits return `-ETIME`.
- Interruptible/killable variants are not present in this file; all contended waits use `TASK_UNINTERRUPTIBLE`.

## Dependencies
Depends on local `linux/sched.h`, spinlock, list, and semaphore definitions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/semaphore.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/seq_buf.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/seq_buf.c

## Purpose
Minimal Linux `seq_buf` formatter implementation.

## Key Responsibilities
- Appends formatted strings with `seq_buf_vprintf()` and `seq_buf_printf()`.
- Appends strings, characters, and raw memory with `seq_buf_puts()`, `seq_buf_putc()`, and `seq_buf_putmem()`.
- Marks overflow via `seq_buf_set_overflow()`.

## Behavior
- Functions return `0` on success and `-1` on overflow.
- `seq_buf_puts()` preserves a trailing NUL in storage but does not count it in `s->len`.
- Warns if used with a zero-sized buffer.

## Dependencies
Uses `linux/seq_buf.h`, libc `stdio.h`, and standard string/memory routines.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/seq_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/shrinker.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/shrinker.c

## Purpose
Userspace implementation of Linux shrinker registration and background memory-pressure scanning.

## Key Responsibilities
- Allocates, registers, unregisters, and frees `struct shrinker`.
- Maintains a global `shrinker_list` protected by `shrinker_lock`.
- Runs shrinkers when allocation fails or when free memory falls below a target.
- Starts a background `shrinkers` kthread in `linux_shrinkers_init()`.

## Behavior
- Allocation-failure mode scans one eighth of counted objects.
- Periodic mode targets roughly 6 percent physical RAM free, adjusted by swap availability.
- The shutdown destructor is disabled because stopping the shrinker thread was observed to segfault rarely.

## Dependencies
Uses kthreads, mutexes, list APIs, percpu init, block device init, `si_meminfo()`, futex waits, and bcachefs `tools-util.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/shrinker.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/siphash.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/siphash.c

## Purpose
Linux SipHash/HalfSipHash implementation for keyed hash/PRF use.

## Key Responsibilities
- Implements SipHash2-4 for secure 64-bit keyed hashing.
- Implements HalfSipHash1-3 / SipHash1-3 variants for hash-table use.
- Provides aligned and, when needed, unaligned implementations.
- Provides fixed-argument helpers for 1-4 `u64` and selected `u32` inputs.

## Important APIs
- `__siphash_aligned()`, `__siphash_unaligned()`
- `siphash_1u64()` through `siphash_4u64()`
- `siphash_1u32()`, `siphash_3u32()`
- `__hsiphash_aligned()`, `__hsiphash_unaligned()`
- `hsiphash_1u32()` through `hsiphash_4u32()`

## Implementation Notes
- 64-bit builds implement HalfSipHash using a reduced-round 64-bit SipHash path for performance.
- 32-bit builds implement true 32-bit HalfSipHash rounds.
- Tail bytes are folded with little-endian loads or byte-by-byte switch fallthrough.
- Exports symbols for kernel-compatible linkage.

## Dependencies
Uses `linux/siphash.h`, bit operations, unaligned access helpers, and optional word-at-a-time dcache helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/siphash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/sort.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/sort.c

## Purpose
Kernel-style non-recursive heapsort implementation.

## Key Responsibilities
- Implements `sort_r()` with optional private data passed to comparator/swapper.
- Chooses optimized default swap routines for 64-bit words, 32-bit words, or bytes.
- Supports wrapper compatibility for traditional `sort()`-style comparator/swap signatures.

## Algorithm
- Bottom-up heapsort.
- O(n log n) average and worst-case behavior.
- Reduces comparator calls by finding the sift-down path to leaves before backtracking.

## Important Details
- `is_aligned()` chooses word-wide swapping only when element size and base alignment permit it.
- `parent()` computes byte-offset parents without full division at each step.
- Built-in swapping avoids slower indirect calls when possible.

## Dependencies
Uses `linux/sort.h`, compiler/type/export helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/stacktrace.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/stacktrace.c

## Purpose
Userspace implementation of `stack_trace_save_tsk()` using libunwind.

## Key Responsibilities
- Captures stack traces from the current thread directly.
- Captures stack traces from another thread by delivering `SIGRTMIN` and unwinding inside the target thread's signal handler.
- Serializes cross-thread backtrace requests with a global mutex and single in-flight request slot.

## Implementation Notes
- Uses `pthread_once()` to install the signal handler.
- Skips the signal-handler/current helper frame plus requested `skipnr`.
- Busy-waits with `sched_yield()` until the target handler marks the request done.
- Intended for debug paths, not high-contention tracing.

## Dependencies
Requires libunwind, pthreads, signals, and local `task_struct.thread`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/stacktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/string.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/string.c

## Purpose
Small subset of Linux string/memory helpers.

## Key APIs
- `strim()` trims leading and trailing whitespace in place.
- `strlcpy()` copies with truncation and returns source length.
- `strscpy()` copies with Linux-style `-E2BIG` on truncation/invalid count.
- `memzero_explicit()` clears memory and uses `barrier_data()`.
- `match_string()` returns the index of a matching string or `-EINVAL`.
- `memscan()` returns pointer to first matching byte or end pointer.

## Dependencies
Uses libc ctype/string/errno/limits plus Linux bug/compiler/string headers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/string.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/string_helpers.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/string_helpers.c

## Purpose
Linux `string_get_size()` helper for human-readable byte/block size formatting.

## Behavior
- Supports decimal (`B`, `kB`, `MB`, ...) and binary (`B`, `KiB`, `MiB`, ...) units.
- Produces 3 significant figures with decimal rounding.
- Handles large `size * blk_size` products by logarithmically reducing operands before multiplication.
- Outputs `"UNK"` if unit index exceeds the known table.

## API
- `string_get_size(u64 size, u64 blk_size, enum string_size_units units, char *buf, int len)`

## Dependencies
Uses Linux math/division/string helper headers and exports the symbol.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/string_helpers.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/timer.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/timer.c

## Purpose
Userspace kernel timer-list implementation backed by a pthread/kthread and min-heap.

## Key Responsibilities
- Maintains pending timers ordered by expiration jiffies.
- Implements `mod_timer()`, `del_timer()`, `timer_delete_sync()`, and `flush_timers()`.
- Starts the timer worker lazily on first `mod_timer()`.
- Runs callbacks outside the timer mutex and tracks callback execution with `timer_seq`.

## Implementation Notes
- Heap grows by doubling via `realloc()`.
- `timer_delete_sync()` removes pending timer and waits for an in-flight callback generation to finish.
- Timer wait uses `pthread_cond_timedwait()` against `CLOCK_REALTIME` after converting jiffies to nanoseconds.
- Constructor initializes heap capacity to 64.

## Dependencies
Uses pthread mutex/condition variables, local kthread helpers, jiffies/time helpers, and Linux timer API types.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/timer.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-core.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-core.c

## Purpose
High-level Linux Unicode normalization and casefolding helpers.

## Key APIs
- `utf8_validate()`
- `utf8_strncmp()`
- `utf8_strncasecmp()`
- `utf8_strncasecmp_folded()`
- `utf8_casefold()`
- `utf8_normalize()`
- `utf8_load()`
- `utf8_unload()`

## Behavior
- Uses NFDI for validation/normalization and NFDICF for case-insensitive comparison/folding.
- Cursor-based functions compare normalized byte streams.
- `utf8_load()` allocates a `unicode_map`, checks the requested Unicode version, and selects versioned normalization tables.
- Returns `-EINVAL` for invalid cursors/input or unsupported table versions.

## Dependencies
Depends on generated `utf8_data_table` and lower-level cursor/trie functions from `utf8-norm.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-core.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-norm.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-norm.c

## Purpose
Core UTF-8 validation, normalization, casefold decomposition, and canonical combining class ordering engine.

## Key Responsibilities
- Validates UTF-8 sequences through a compact trie.
- Looks up Unicode data leaves for selected normalization tables.
- Computes normalized length with `utf8nlen()`.
- Initializes cursors with `utf8ncursor()`.
- Emits normalized bytes incrementally with `utf8byte()`.
- Handles Hangul syllable decomposition algorithmically.

## Important Structures
- `utf8trie_t`: compact binary trie used to validate and classify UTF-8 sequences.
- `utf8leaf_t`: embedded leaf containing Unicode generation, canonical combining class, and optional decomposition string.
- `utf8cursor`: streaming state machine for normalized output.

## Algorithm Notes
- Rejects invalid UTF-8, continuation-byte starts, overlong/non-table sequences, and unsupported code points.
- Code points newer than the selected table max age are treated as undecomposed with CCC 0.
- Decomposition can redirect cursor input to an embedded decomposition string.
- Combining marks are emitted in canonical combining class order by repeated scans between stoppers.
- Hangul decomposition uses Unicode Section 3.12 constants and synthesizes a temporary leaf.

## Dependencies
Uses `utf8n.h` and generated Unicode tables.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-norm.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8n.h -->
# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8n.h

## Purpose
Private declarations for the UTF-8 normalization implementation.

## Contents
- Declares `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`.
- Defines `UTF8HANGULLEAF`.
- Defines `struct utf8cursor`.
- Defines `struct utf8data` and `struct utf8data_table`.
- Declares external `utf8_data_table`.

## Integration Notes
This header connects high-level Unicode helpers in `utf8-core.c` with trie/cursor internals in `utf8-norm.c` and generated normalization data.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/unicode/utf8n.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/wait.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/wait.c

## Purpose
Userspace implementation of Linux waitqueues, bit waits, and completions.

## Key APIs
- `wake_up()`, `wake_up_all()`
- `prepare_to_wait()`, `finish_wait()`
- `default_wake_function()`, `autoremove_wake_function()`
- `wake_up_bit()`, `__wait_on_bit()`, `out_of_line_wait_on_bit_timeout()`, `__wait_on_bit_lock()`
- `complete()`, `wait_for_completion()`, `wait_for_completion_timeout()`

## Behavior
- Waitqueues are protected by spinlocks and use list entries.
- Exclusive waits are queued at the tail and stop after the requested number of exclusive wakeups.
- Bit waits share one global `bit_wq` and match on `(word, bit_nr)`.
- Completions decrement `done` when consumed.

## Dependencies
Depends on local scheduler, waitqueue, wait-bit, completion, list, bit, and spinlock shims.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/wait.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/workqueue.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/workqueue.c

## Purpose
Userspace workqueue/delayed-work implementation.

## Key Responsibilities
- Allocates named workqueues and starts worker kthreads lazily.
- Implements immediate and delayed work queueing.
- Supports flushing, canceling, modifying delayed work, draining, and destruction.
- Initializes global system workqueues in a constructor.

## Key APIs
- `queue_work()`
- `queue_delayed_work()`
- `mod_delayed_work()`
- `flush_work()`
- `cancel_work_sync()`
- `cancel_delayed_work()`, `cancel_delayed_work_sync()`
- `drain_workqueue()`
- `destroy_workqueue()`
- `alloc_workqueue()`

## Implementation Notes
- One global mutex serializes all workqueue state.
- Work pending state is stored in `WORK_PENDING_BIT`.
- Delayed work uses `timer_list`; timer callback enqueues the work.
- `grab_pending()` handles races between pending list, delayed timer, and running work.
- Constructor creates `system_wq`, `system_highpri_wq`, `system_long_wq`, `system_unbound_wq`, and `system_freezable_wq`.

## Dependencies
Uses local kthread, timer, workqueue, list, slab, and error-name helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/workqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/xxhash.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/xxhash.c

## Purpose
Linux-compatible xxHash implementation, dual BSD/GPL licensed.

## Key APIs
- `xxh32()`, `xxh64()`
- `xxh32_reset()`, `xxh64_reset()`
- `xxh64_update()`, `xxh64_digest()`
- `xxh32_copy_state()`, `xxh64_copy_state()`

## Behavior
- Implements one-shot 32-bit and 64-bit xxHash.
- Implements streaming 64-bit update/digest.
- Uses unaligned little-endian loads.
- Validates streaming update input, returning `-EINVAL` for `NULL`.

## Dependencies
Uses Linux unaligned access, errno, compiler, kernel, module, string, and `xxhash.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/xxhash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/zstd_compress_module.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/zstd_compress_module.c

## Purpose
Linux zstd compression API wrapper over the upstream/new zstd API.

## Key APIs
- `zstd_min_clevel()`, `zstd_max_clevel()`
- `zstd_compress_bound()`
- `zstd_get_params()`
- `zstd_cctx_workspace_bound()`, `zstd_init_cctx()`, `zstd_compress_cctx()`
- `zstd_cstream_workspace_bound()`, `zstd_init_cstream()`
- `zstd_reset_cstream()`, `zstd_compress_stream()`, `zstd_flush_stream()`, `zstd_end_stream()`

## Implementation Notes
- `zstd_cctx_init()` resets the context, sets pledged source size, then maps Linux zstd parameter structs to `ZSTD_CCtx_setParameter()`.
- `pledged_src_size == 0` is translated to `ZSTD_CONTENTSIZE_UNKNOWN` for stream init.
- Static contexts are initialized from caller-provided workspaces.

## Dependencies
Uses `linux/zstd.h` and exports Linux-compatible symbols.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/zstd_compress_module.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/zstd_decompress_module.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/zstd_decompress_module.c

## Purpose
Linux zstd decompression/common API wrapper over upstream zstd.

## Key APIs
- `zstd_is_error()`, `zstd_get_error_code()`, `zstd_get_error_name()`
- `zstd_dctx_workspace_bound()`, `zstd_init_dctx()`, `zstd_decompress_dctx()`
- `zstd_dstream_workspace_bound()`, `zstd_init_dstream()`
- `zstd_reset_dstream()`, `zstd_decompress_stream()`
- `zstd_find_frame_compressed_size()`, `zstd_get_frame_header()`

## Implementation Notes
- Static decompression contexts are created from caller workspaces.
- `max_window_size` is accepted for API compatibility but ignored by `zstd_init_dstream()` in this wrapper.

## Dependencies
Uses `linux/zstd.h` and exports Linux-compatible symbols.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/zstd_decompress_module.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/make-release-tarball.sh -->
# File Research: sources/cow-pools/bcachefs-tools/make-release-tarball.sh

## Purpose
Manual release script for producing and publishing bcachefs-tools source tarballs.

## Workflow
- Checks out tag `v$version`.
- Cleans the tree and runs `make generate_version`.
- Generates Rust dependency license text with `cargo license`.
- Creates `bcachefs-tools-$version.tar` from git-tracked files plus generated `version.h` and license file.
- Compresses with `zstd --ultra`.
- Produces detached and clear-signed GPG signatures.
- Uploads artifacts to `evilpiepirate.org`.
- Runs `cargo-vendor-filterer`.
- Creates `.cargo/config.toml` pointing crates.io and a custom bindgen git source to `vendor`.
- Builds and publishes a vendored tarball variant.

## Dependencies
Requires git, make, cargo license, zstd, gpg, scp, and cargo-vendor-filterer.

## Notes
The script assumes release infrastructure paths and GPG identity are already configured locally.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/make-release-tarball.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/mount.bcachefs.sh -->
# File Research: sources/cow-pools/bcachefs-tools/mount.bcachefs.sh

## Purpose
Mount helper wrapper for bcachefs that expands a filesystem UUID into device paths.

## Behavior
- Parses mount options with `getopt`.
- Locates the first non-option positional argument as `UUID`.
- If the argument looks like a 32-hex UUID with optional dashes, scans `/proc/partitions`.
- Runs `bcachefs show-super /dev/$part` with a timeout and collects devices whose superblock output matches the UUID.
- Replaces the UUID argument with a colon-separated device list.
- Executes `mount -i -t bcachefs` with the rewritten arguments.

## Failure Modes
- Exits if UUID scan finds no matching devices.
- Prints a generic argument error when `getopt` fails.

## Dependencies
Requires bash, getopt, awk, timeout, bcachefs, and mount.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/mount.bcachefs.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/Cargo.toml -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/Cargo.toml

## Purpose
Rust package manifest for the bcachefs package CI orchestrator.

## Contents
- Workspace root and binary package `bcachefs-package-ci`.
- Rust edition 2021.
- Binary entrypoint at `src/main.rs`.

## Dependencies
- `anyhow`
- `log`
- `env_logger`
- `serde`, `serde_json`
- `chrono` with clock support
- `libc`
- `signal-hook`

## Integration
This manifest builds the filesystem-backed Debian package CI daemon described in `src/main.rs`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/Cargo.toml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/bcachefs-package-ci.service -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/bcachefs-package-ci.service

## Purpose
Systemd unit for running the bcachefs-tools package CI orchestrator.

## Behavior
- Runs as user `aptbcachefsorg`.
- Executes `/home/aptbcachefsorg/package-ci/bcachefs-package-ci`.
- Restarts on failure after 30 seconds.
- Sends logs to journald with identifier `bcachefs-package-ci`.
- Sets `RUST_LOG=info`, `XDG_RUNTIME_DIR`, and `HOME`.

## Notes
No additional systemd sandboxing is used because rootless podman handles namespaces and the service already runs unprivileged.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/bcachefs-package-ci.service -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary-remote.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary-remote.sh

## Purpose
Remote wrapper for binary `.deb` builds, intended for arm64 builds on `farm1`.

## Workflow
- Accepts host, distro, arch, commit, source dir, result dir, and Rust version.
- Creates remote work directories under `/tmp/bcachefs-ci/$commit/$distro-$arch`.
- Copies source artifacts and `build-binary.sh` to the remote host.
- Runs the normal binary build script remotely.
- Copies result artifacts back.
- Removes the remote work directory.

## Dependencies
Requires ssh/scp access and matching build scripts on the local side.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary-remote.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary.sh

## Purpose
Build binary Debian packages for one distro/architecture pair inside podman.

## Supported Inputs
- Distros: `unstable`, `forky`, `trixie`, `plucky`, `questing`
- Architectures: `amd64`, `ppc64el`, `arm64`
- Source directory containing a `.dsc`
- Result directory
- Rust version

## Workflow
- Selects a Debian/Ubuntu base image.
- Enables ppc64el cross-build setup when needed.
- Finds the source `.dsc`.
- Builds or reuses a cached podman image keyed by distro, arch, Rust version, and cache version.
- Installs build-essential, devscripts, dpkg tools, build dependencies, and cross tools.
- Installs rustup Rust if the distro Rust is older than required.
- Adds cargo cross-linker config for ppc64el.
- Runs `dpkg-buildpackage -b`.
- Copies `.deb`, `.ddeb`, `.changes`, and `.buildinfo` to result dir.

## Implementation Notes
- Cache rebuild can be forced by `REBUILD_CACHE=1` or marker files.
- Uses `seccomp=unconfined`, `apparmor=unconfined`, `/dev/fuse`, and `SYS_ADMIN` for the build container.
- Caps parallelism through `DEB_BUILD_OPTIONS=parallel=$MAX_PARALLEL`, default 16.
- Works around Debian's cargo wrapper discarding `RUSTFLAGS` by writing `.cargo/config.toml`.

## Dependencies
Requires podman, apt, dpkg-dev/devscripts, rustup as needed, and cross-compilation packages for ppc64el.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-source.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-source.sh

## Purpose
Build source-only Debian package artifacts for a target commit.

## Workflow
- Clones the bcachefs-tools git repo into a temporary workdir.
- Checks out the requested commit.
- Computes package version from exact tag, latest tag, `.version`, commit hash, and UTC snapshot timestamp.
- Preserves a Debian epoch from `debian/changelog` if present.
- Starts a `debian:trixie-slim` podman container with cached rustup/cargo/apt directories.
- Installs source-build dependencies.
- Installs or updates rustup to the configured Rust version.
- Installs `cargo-vendor-filterer` if missing.
- Updates changelog with `dch`.
- Runs `dpkg-buildpackage -d -S -us -uc -nc`.
- Copies source artifacts to the result directory.

## Dependencies
Requires podman, git, Debian packaging tools, rustup, cargo-vendor-filterer, and network access for apt/cargo.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-source.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/generate-status-html.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/generate-status-html.sh

## Purpose
Generate a static CI status page at `$PUBLIC_HTML/ci.html`.

## Behavior
- Reads desired commit from `$STATE_DIR/desired`.
- Iterates build directories newest-first.
- For each commit, renders a table of job statuses except the source job.
- Links each job to `/ci-builds/$commit/$job/log`.
- Summarizes done/failed/building counts.
- Adds auto-refresh every 30 seconds and an updated UTC timestamp.
- Writes atomically through a temporary file then `mv`.

## Dependencies
Requires shell access to the CI state directory and public HTML directory.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/generate-status-html.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/post-receive -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/post-receive

## Purpose
Git server post-receive hook that queues CI builds.

## Behavior
- Watches pushes to `refs/heads/master` and tags matching `refs/tags/v*`.
- Writes the target commit hash to `$STATE_DIR/desired`.
- Signals the orchestrator with `SIGUSR1` using `$STATE_DIR/orchestrator.pid` if present.
- Resolves annotated tags to their commit via `git rev-parse "$newrev^{commit}"`.

## Integration
This is the event source for the reconcile-loop CI daemon. There is no queue; the desired file always points to the latest requested commit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/post-receive -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/publish.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/publish.sh

## Purpose
Publish built bcachefs-tools Debian packages to apt.bcachefs.org.

## Workflow
- Loads signing and publish config from `$STATE_DIR/config`.
- Signs `.deb` and `.ddeb` artifacts with `debsigs`.
- Detects distro jobs with status `done`.
- Creates or updates aptly repos named `$distro-$suite`.
- Removes old `bcachefs-*` packages before adding new artifacts.
- Adds source and binary artifacts with `aptly repo add`.
- Creates snapshots and publishes or switches aptly publications.
- Syncs staging to live with `rsync --delay-updates`.
- Exports GPG public key in binary and armored forms.
- Generates nginx fancyindex footer instructions for users.

## Important Notes
- Avoids aptly `-force-overwrite` because it can corrupt shared pool files by overwriting in place.
- Does not use `rsync --delete`, preserving suites not published in the current run.
- Suite is `snapshot` by default or `release` for tagged releases.

## Dependencies
Requires aptly, gpg, debsigs, rsync, and a configured signing subkey.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/publish.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/setup-epp.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/setup-epp.sh

## Purpose
One-time setup script for package CI on `evilpiepirate.org`.

## Workflow
- Requires root.
- Installs podman, sbuild, mmdebstrap, aptly, gnupg, devscripts, git-buildpackage, qemu-user-static, and uidmap.
- Configures subuid/subgid ranges for `aptbcachefsorg`.
- Creates CI directories and cache directories.
- Installs the git post-receive hook if absent.
- Installs and enables the systemd service.
- Prints manual follow-up deployment and GPG setup steps.

## Notes
The script does not build or deploy the Rust orchestrator binary itself; it documents those as next steps.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/setup-epp.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/status.sh -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/status.sh

## Purpose
Command-line status reporter for package CI builds.

## Behavior
- Uses explicit commit argument or reads `$STATE_DIR/desired`.
- Validates that the commit build directory exists.
- Iterates job directories and prints status rows.
- Counts done, failed, building, and pending jobs.

## Notes
The script emits human-readable status symbols for done/failed/building/pending.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/scripts/status.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/src/main.rs -->
# File Research: sources/cow-pools/bcachefs-tools/package-ci/src/main.rs

## Purpose
Rust daemon implementing a self-hosted Debian package CI orchestrator for bcachefs-tools.

## Architecture
- Filesystem-backed reconcile loop under `$STATE_DIR`.
- Desired target commit is read from `desired`.
- Per-commit state is stored under `builds/$commit`.
- Each job has `status`, timestamped logs, stable `log` symlink, optional `pid`, and result directory.
- No queue: the daemon continuously reconciles desired state against existing filesystem state.

## Build Matrix
- Distros: `unstable`, `forky`, `trixie`, `questing`, `plucky`.
- Architectures: `amd64`, `ppc64el`, `arm64`.
- Ubuntu ppc64el is skipped because cross-build is marked broken.
- arm64 jobs are remote; ppc64el is local cross-compile.

## Job Phases
1. Source package build.
2. Binary builds across the distro/arch matrix.
3. Publish successful outputs, even if some builds failed.

## Key Types
- `Distro`, `Arch`, `Job`
- `JobStatus`
- `BuildState`
- `Config`
- `RunningJob`
- `Orchestrator`
- `Signals`

## Important Behavior
- `effective_status()` detects stale `building` jobs by checking tracked children and `kill(pid, 0)`, then marks dead jobs failed.
- `reap_children()` updates statuses on child exit and kills builds exceeding the configured timeout.
- Local/remote concurrency is limited independently.
- Logs are redirected to per-job files.
- Tagged commits publish to `release`; other commits publish to `snapshot`.
- `SIGUSR1` wakes the loop, while SIGTERM/SIGINT trigger shutdown and child termination.
- Writes `orchestrator.pid` on startup and removes it on shutdown.

## Default Config
- Git repo: `/var/www/git/bcachefs-tools.git`
- State dir: `/home/aptbcachefsorg/package-ci`
- Scripts dir: `/home/aptbcachefsorg/package-ci/scripts`
- arm64 host: `farm1.evilpiepirate.org`
- Rust version: `1.89.0`
- Max local jobs: 2
- Max remote jobs: 1
- Poll interval: 60 seconds
- Build timeout: 2 hours

## Dependencies
Uses `anyhow`, `chrono`, `log`, `env_logger`, `libc`, and `signal-hook`, plus external shell scripts in `package-ci/scripts`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/package-ci/src/main.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/check.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/check.c

## Purpose
RAID parity validation and failure scanning.

## Key APIs
- `raid_check()`
- `raid_scan()`

## Core Logic
- `raid_validate()` validates failed data blocks using extra valid parity blocks.
- Builds a coefficient matrix from `A(parity, disk)` values.
- Inverts the matrix with `raid_invert()`.
- Uses multiplication tables to reconstruct suspected data bytes.
- Verifies remaining parity equations reduce to zero.

## Behavior
- `raid_check()` accepts failed indexes across data and parity blocks, identifies valid parity indexes, and validates data failures.
- `raid_scan()` brute-forces combinations of possible failures and returns the first valid set size and indexes.
- Requires `size` to be a multiple of 64.
- Requires number of failed blocks for checking to be strictly less than parity count because an extra parity is needed for validation.

## Dependencies
Uses `internal.h`, `combo.h`, and `gf.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/combo.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/combo.h

## Purpose
Inline helpers for enumerating permutations and combinations.

## APIs
- `permutation_first()`
- `permutation_next()`
- `combination_first()`
- `combination_next()`

## Behavior
- Permutations are with repetition, equivalent to nested loops over `0..n`.
- Combinations are without repetition and return indexes in increasing order.
- `*_next()` returns `0` when enumeration is complete.
- Uses assertions to enforce `0 < r <= n`.

## Usage
Used by RAID scanning/checking paths to test possible failed block sets.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/combo.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/cpu.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/cpu.h

## Purpose
x86 CPU feature detection and microarchitecture heuristics for RAID implementation selection.

## Key Responsibilities
- Wraps `cpuid` and `xgetbv`.
- Extracts CPU vendor, family, and model.
- Detects SSE2, SSSE3, CRC32, AVX2, and AVX512BW capability.
- Checks OS XSAVE/XCR0 state before enabling AVX/AVX512 paths.
- Detects Intel Atom and related slow-operation heuristics.
- Detects slow extended SSE register cases, especially AMD Bulldozer and some Intel Atom models.

## Important APIs
- `raid_cpu_has_sse2()`
- `raid_cpu_has_ssse3()`
- `raid_cpu_has_crc32()`
- `raid_cpu_has_avx2()`
- `raid_cpu_has_avx512bw()`
- `raid_cpu_has_slowmult()`
- `raid_cpu_has_slowextendedreg()`

## Dependencies
Only active under `CONFIG_X86`; relies on inline assembly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/gf.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/gf.h

## Purpose
Inline Galois-field helper operations for RAID parity math.

## APIs / Macros
- `mul()`, `inv()`, `pow2()`, `table()`, `A()`
- `v_8()`, `v_32()`, `v_64()`
- `x2_32()`, `x2_64()`
- `d2_32()`, `d2_64()`

## Behavior
- Field multiplication, inverse, exponent, and generator coefficients are table-driven.
- `x2_*` multiplies each byte lane by 2 in GF(2^8).
- `d2_*` divides each byte lane by 2 in GF(2^8).
- Uses `BUG_ON()` for invalid inverse/exponent input.

## Dependencies
Relies on tables declared in `internal.h`: `gfmul`, `gfinv`, `gfexp`, and `gfgen`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/gf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/helper.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/helper.c

## Purpose
Small helper routines for sorting RAID failure index vectors.

## APIs
- `raid_sort(int n, int *v)`
- `raid_insert(int n, int *v, int i)`

## Behavior
- `raid_sort()` uses fixed sorting networks for vectors of size 2 through 6.
- `raid_insert()` appends a value and swaps backward until sorted.
- Designed for very small vectors up to `RAID_PARITY_MAX`.

## Dependencies
Uses `internal.h` for compatibility macros and constants.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/helper.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/helper.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/helper.h

## Purpose
Public declarations and documentation for RAID index helper routines.

## APIs
- `raid_insert()`
- `raid_sort()`

## Notes
Documents that callers can use these helpers to order indexes before calling recovery routines.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/helper.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/int.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/int.c

## Purpose
Portable integer C implementations of RAID parity generation and data recovery.

## Parity Generation
- `raid_gen1_int32()`, `raid_gen1_int64()`: RAID5 XOR parity.
- `raid_gen2_int32()`, `raid_gen2_int64()`: RAID6 P/Q parity using powers of 2.
- `raid_gen3_int8()` through `raid_gen6_int8()`: triple through six-way parity using Cauchy matrix coefficients.

## Recovery
- `raid_rec1_int8()`: recovers one data block using one chosen parity.
- `raid_rec2_int8()`: recovers two data blocks using two chosen parities.
- `raid_recX_int8()`: generic N-data-block recovery.
- Specialized fast paths are used for common parity choices:
  - `raid_rec1of1()` for RAID5 P parity.
  - `raid_rec2of2_int8()` for RAID6 P/Q recovery.

## Algorithm
- Constructs coefficient matrix from parity and data indexes.
- Inverts matrix over GF(2^8).
- Precomputes multiplication table pointers for inverse coefficients.
- Computes delta parity with `raid_delta_gen()`.
- Reconstructs missing bytes by multiplying delta parity vector by inverse matrix.

## Dependencies
Uses `internal.h` and `gf.h`; relies on field tables and generator matrix.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/int.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/internal.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/internal.h

## Purpose
Private central header for the RAID library.

## Key Responsibilities
- Defines feature/config macros for x86, SSE2, SSSE3, and AVX2 based on config or compiler target.
- Defines compatibility helpers: `BUG_ON`, `__always_inline`, `__aligned`, `__align_ptr`.
- Includes public RAID headers and helper declarations.
- Declares internal functions for parity generation, recovery, inversion, delta generation, and self-test.
- Declares function-pointer dispatch tables for selected implementations.
- Declares Galois-field and pshufb tables.
- Provides SSE/AVX begin/end helpers with memory barriers and register clobbers.

## Important Dispatch Globals
- `raid_gen3_ptr`
- `raid_genz_ptr`
- `raid_gen_ptr[RAID_PARITY_MAX]`
- `raid_rec_ptr[RAID_PARITY_MAX]`

## Dependencies
Includes standard C headers and RAID public headers; conditionally uses inline x86 assembly for SIMD cleanup barriers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/intz.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/intz.c

## Purpose
Portable integer C implementation of GENz triple parity.

## Key APIs
- `raid_genz_int32()`
- `raid_genz_int64()`

## Algorithm
GENz computes:
- P parity as XOR.
- Q parity by multiplying accumulated bytes by 2.
- R parity by dividing accumulated bytes by 2.

The functions process data blocks from last to first and operate on two 32-bit or two 64-bit chunks per loop iteration.

## Dependencies
Uses `internal.h` and `gf.h` for byte-lane GF arithmetic helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/intz.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/memory.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/memory.c

## Purpose
Aligned allocation and memory test/fill helpers for the RAID library.

## APIs
- `raid_malloc_align()`
- `raid_malloc()`
- `raid_malloc_vector_align()`
- `raid_malloc_vector()`
- `raid_mrand_vector()`
- `raid_mtest_vector()`

## Behavior
- Allocates extra memory and returns an aligned pointer while storing the original pointer in `freeptr`.
- Vector allocation creates a pointer array and a contiguous aligned backing region.
- Data-block pointers are reversed to match access patterns that often iterate from last data block downward.
- Random fill uses a simple C99/C11-style linear congruential generator.
- Memory test cycles through byte patterns and complements to detect RAM/data path issues.

## Dependencies
Uses `internal.h` and `memory.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/memory.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/memory.h

## Purpose
Public declarations and constants for RAID memory helpers.

## Constants
- `RAID_MALLOC_ALIGN`: 256-byte alignment.
- `RAID_MALLOC_DISPLACEMENT`: `7 * 256`, used to reduce cache address aliasing across contiguous block buffers.

## APIs
- `raid_malloc()`
- `raid_malloc_align()`
- `raid_malloc_vector()`
- `raid_malloc_vector_align()`
- `raid_mrand_vector()`
- `raid_mtest_vector()`

## Notes
The displacement comment records empirical throughput gains from avoiding cache/prefetch aliasing for multi-buffer RAID operations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/module.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/module.c

## Purpose
RAID implementation initialization and self-test support.

## Initialization
`raid_init()` selects default implementations:
- Portable integer implementations by default.
- SSE2 implementations when available.
- SSSE3 implementations for higher parity and recovery when available.
- AVX2 implementations when available.
- Uses CPU heuristics to choose extended-register or non-extended variants.
- Sets default mode to `RAID_MODE_CAUCHY`.

## Reference Generation
`raid_gen_ref()` computes parity byte-by-byte using generic GF multiplication and the selected generator matrix. It serves as correctness oracle for tests.

## Self-Test
`raid_selftest()`:
- Allocates aligned buffers.
- Uses the GF multiplication table as deterministic test data.
- Computes reference parity for maximum parity.
- Tests parity generation for each parity level.
- Tests recovery of ending data failures.
- Tests recovery with mixed data/parity failures.
- Tests data-only recovery using selected parity blocks.
- Tests scan detection with corrupted data/parity.
- Verifies no-parity scan failure.

## Dependencies
Uses `internal.h`, `memory.h`, and `cpu.h`, plus all generated/optimized RAID implementations through dispatch tables.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/module.c -->