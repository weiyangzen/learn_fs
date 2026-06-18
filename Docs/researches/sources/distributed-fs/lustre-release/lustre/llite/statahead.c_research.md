<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/statahead.c -->
# sources/distributed-fs/lustre-release/lustre/llite/statahead.c

## Purpose
`statahead.c` implements llite metadata stat-ahead for directory traversal and regular numeric filename patterns. It predicts future child lookups, issues asynchronous metadata `getattr` intent RPCs, caches prepared `sa_entry` results by name, and optionally runs an asynchronous glimpse-lock (AGL) helper for regular files so later size/glimpse-sensitive paths avoid synchronous round trips.

## Important APIs, Types, And Functions
Core state is `struct sa_entry`, `struct ll_statahead_info`, and `struct ll_statahead_context`. Important entry points are `ll_authorize_statahead()`, `ll_deauthorize_statahead()`, `ll_start_statahead()`, `ll_revalidate_statahead()`, `ll_ioctl_ahead()`, and `ll_statahead_enter()`. The main workers are `ll_statahead_thread()` and `ll_agl_thread()`. `sa_alloc()`, `sa_get()`, `sa_put()`, `sa_make_ready()`, `sa_lookup()`, and `sa_revalidate()` manage cached predictions and async RPC completion.

## Control Flow
Directory open authorizes list-pattern statahead. The first stat on an eligible child calls `start_statahead_thread()`, which detects list or numeric filename patterns, allocates `sai`/`sax`, optionally starts AGL, and returns `-EAGAIN` so the triggering lookup proceeds normally. The worker scans directory pages or synthesizes names, calls `sa_statahead()`, and sends either batched metadata updates through `md_batch_add()` or direct `md_intent_getattr_async()`. Async callbacks run `ll_statahead_interpret()`, defer dangerous inode preparation to workqueue context when needed, install lock data, cache encryption context, and mark the `sa_entry` ready. Lookup revalidation later calls `ll_revalidate_statahead()` to splice or validate the cached inode and consume the entry.

## State And Persistence
State is in-memory only. Per-inode `lli_sai`, `lli_sax`, `lli_sa_pattern`, generation counters, locks, hidden-file counters, filename prediction counters, and cached `sa_entry` lists persist while a directory handle or advise request is active. `sai_hit`, `sai_miss`, `sai_sent`, `sai_replied`, `sai_cache_count`, and window `sai_max` tune behavior. Memory ordering around `sai_task` and `se_state` is explicit with acquire/release barriers; entries are freed after scanner use or worker shutdown.

## Dependencies And Integration Points
The file integrates with llite lookup/revalidate, directory-page reads, llcrypt name translation, MDC async intent getattr, MDC batch RPCs, LDLM intent locks, `ll_prep_inode()`, xattr cache insertion for encryption contexts, AGL via `cl_agl()`, and llite mount tunables such as `ll_sa_max`, `ll_sa_min`, batch limits, timeouts, and running limits.

## Risks And Edge Cases
The highest risks are races among lookup consumers, async RPC callbacks, worker shutdown, and directory close. Wrong-PID cache hits stop the worker, stale FID replies are rejected, low hit ratios disable statahead, and in-use entries delay final cleanup. Hidden file handling is adjusted when `ls -al` appears after skipped dot entries. The ptlrpcd callback avoids blocking inode preparation for striped directories and layout changes by scheduling work.

## Test Signals
Useful signals include `ls -l` and `ls -al` on large directories, mdtest-style numeric stat workloads, shared-directory multi-process patterns, ladvise ahead ranges, encrypted directory names, batch-RPC-capable and non-capable MDT connections, AGL enabled/disabled mounts, low-hit-ratio stop paths, close while RPCs are in flight, and fault injections for stale layout, pause, allocation, and async completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/statahead.c -->
