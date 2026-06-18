# Group Research: group_1173_nbdkit_sources_virtualization_nbdkit_filters_map_Makefile_am_source_fbc6ff19c127

Scope: `Docs/research_subset_a.md`; source tree `sources/virtualization/nbdkit`. Every source listed in this grouped work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/map/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/map/Makefile.am

This Automake fragment builds `nbdkit-map-filter.la` from `map.c` and the public filter header, distributes `nbdkit-map-filter.pod`, and generates `nbdkit-map-filter.1` plus HTML through `podwrapper.pl` when POD support is enabled. It includes common nbdkit build rules and wires include paths for core headers, `common/regions`, and `common/utils`.

The filter links against `libregions.la`, `libutils.la`, compatibility replacements, and the Windows import library when applicable. It uses module-style libtool flags with optional linker-version script support via `filters/filters.syms`.

Integration risk is mostly build-contract drift: `map.c` depends on the regions and utility helpers named here, so changes to range mapping helpers or Windows no-undefined behavior must keep these library and include dependencies in sync.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/map/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/map/map.c -->
# File Research: sources/virtualization/nbdkit/filters/map/map.c

This filter remaps the visible virtual address space onto arbitrary byte ranges in the underlying plugin. It parses `map=START-END:DEST` rules and optional `map-size=SIZE`, appends an implicit low-priority identity mapping, then converts potentially overlapping command-line ranges into a complete non-overlapping `regions` table. Earlier command-line mappings get higher priority through a descending `prio` value, and debug output is controlled by `-D map.ranges=1`.

The core algorithm collects all start and end+1 boundaries, splits every original range at those boundaries, sorts ranges by virtual start, removes lower-priority duplicates at identical positions, asserts there are no gaps, and appends region entries whose `u.i` points back to the selected range. `do_mapping` is the shared execution engine for reads, writes, trims, zeroes, cache requests, and extents; it walks regions, translates virtual offsets to each range's destination offset, checks against the current plugin size, and invokes an operation-specific callback.

Read/write/cache/trim/zero handlers are thin wrappers around `do_mapping`. The extents handler allocates a temporary extents object for the underlying mapped range and translates returned extent offsets back into the caller-visible virtual coordinate space before adding them to the output object.

Important edge cases are inclusive end offsets, `end == start` being a one-byte range, `INT64_MAX` sentinel ranges, and runtime `next->get_size` checks that reject mapped I/O beyond the backend. The code assumes region conversion succeeds before serving requests; most malformed configuration failures call `exit(EXIT_FAILURE)` during config parsing or completion, consistent with nbdkit filter startup behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/map/map.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/multi-conn/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/multi-conn/Makefile.am

This fragment builds `nbdkit-multi-conn-filter.la` from `multi-conn.c`, distributes its POD manual, and creates the manual page through the shared POD wrapper when enabled. Include paths cover nbdkit public headers, generated headers, `common/include`, and `common/utils`.

It links `libutils.la`, compatibility replacements, and the Windows import library, then uses module/no-version/shared libtool flags with optional linker-script export restriction. The file is purely build glue for the multi-connection consistency filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/multi-conn/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/multi-conn/multi-conn.c -->
# File Research: sources/virtualization/nbdkit/filters/multi-conn/multi-conn.c

This filter controls and emulates NBD multi-connection consistency. Configuration accepts `multi-conn-mode` (`auto`, `emulate`, `plugin`, `disable`, `unsafe`), `multi-conn-track-dirty` (`conn`, `fast`, `off`), and optional grouping by export name through `multi-conn-exportname` / `multi-conn-export-name`.

Runtime state is organized into `handle` objects for active connections and `group` objects for sets of connections that should be flushed together. A global mutex protects group membership and dirty-state updates that must be coordinated. `AUTO` resolves in `.prepare`: if the backend advertises multi-conn, the filter delegates to the plugin; otherwise it emulates by requiring backend flush support. `.get_ready` disables auto emulation under `SERIALIZE_CONNECTIONS`.

I/O wrappers mark dirty state on reads, cache requests, writes, zeroes, and trims. FUA writes/zeroes/trims in emulation mode are downgraded to ordinary operations followed by a coordinated flush. `multi_conn_flush` is the central consistency operation: in emulation mode it flushes all dirty peer connections in the group; otherwise it may skip flushes if dirty tracking says the image is clean, or clear dirty state after a successful backend flush.

Behavioral risks center on dirty tracking precision. `CONN` is more accurate but tracks read/write state per connection; `FAST` tracks only group write dirtiness; `OFF` always flushes broadly. The code deliberately avoids locking in `mark_dirty`, relying on NBD client ordering around flush responses, so misuse by clients issuing flushes concurrently with dependent commands can produce races outside the filter's guarantees.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/multi-conn/multi-conn.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nocache/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/nocache/Makefile.am

This Automake file builds the `nocache` filter module from `nocache.c`, installs/distributes the POD manual, and optionally generates the man page. It includes only the core nbdkit include directories needed by this small capability-shaping filter.

The library has no common helper library dependency beyond the platform import library. It applies the standard module, no-version, shared, and optional linker-script flags used by nbdkit filters.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nocache/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nocache/nocache.c -->
# File Research: sources/virtualization/nbdkit/filters/nocache/nocache.c

This filter changes how the server advertises and handles `NBD_CMD_CACHE`. The `cache-mode` / `cachemode` parameter accepts `none` (default), `emulate`, and `nop` / `no-op`.

`nocache_can_cache` maps those modes to `NBDKIT_CACHE_NONE`, `NBDKIT_CACHE_EMULATE`, or `NBDKIT_CACHE_NATIVE`. In `NOP` mode the filter advertises native cache support but implements `.cache` as a no-op that returns success, requiring zero flags and asserting that the mode is active.

The filter has intentionally narrow behavior: it does not pass cache requests to the backend, and it does not alter ordinary reads or writes. Its main risk is semantic: `nop` can make clients believe cache hints are honored even though they are intentionally ignored.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nocache/nocache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/noextents/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/noextents/Makefile.am

This build fragment creates `nbdkit-noextents-filter.la` from `noextents.c`, includes the public/generated nbdkit headers, and wires the standard filter module flags. It distributes and optionally builds the `nbdkit-noextents-filter.1` manual.

There are no common helper libraries linked beyond the platform import library, reflecting that the implementation only changes one advertised capability.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/noextents/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/noextents/noextents.c -->
# File Research: sources/virtualization/nbdkit/filters/noextents/noextents.c

This minimal filter disables extent support by implementing `.can_extents` to return `0`. It registers the filter under the name `noextents` and otherwise leaves all operations to normal nbdkit filter fallback behavior.

The effect is capability shaping: clients will not see block-status/extents support even if the underlying plugin supports it. There is no per-connection state and no request-path transformation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/noextents/noextents.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nofilter/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/nofilter/Makefile.am

This fragment builds a do-nothing `nbdkit-nofilter-filter.la` from `nofilter.c`, with core include paths and the normal filter module/linker flags. It distributes and optionally generates the `nbdkit-nofilter-filter.1` manual.

The module links only the platform import library because the implementation has no helper dependencies. It exists as a build/test/demo baseline for an empty filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nofilter/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nofilter/nofilter.c -->
# File Research: sources/virtualization/nbdkit/filters/nofilter/nofilter.c

This file registers an nbdkit filter named `nofilter` with only `.name` and `.longname` set. It implements no callbacks, so nbdkit's normal filter passthrough behavior applies to all capabilities and requests.

The file is useful as a minimal filter skeleton or behavior-control placeholder. It carries no state, no configuration, and no direct operational risk beyond adding an extra module layer.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nofilter/nofilter.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/noparallel/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/noparallel/Makefile.am

This build file creates `nbdkit-noparallel-filter.la` from `noparallel.c`, distributes the POD manual, and optionally emits `nbdkit-noparallel-filter.1`. It uses the core include paths and standard filter module flags.

The implementation is self-contained and links only the platform import library. Build risk is low; the important dependency is the public filter API's thread-model callback contract.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/noparallel/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/noparallel/noparallel.c -->
# File Research: sources/virtualization/nbdkit/filters/noparallel/noparallel.c

This filter reduces nbdkit's thread model at runtime. Configuration key `serialize` / `serialise` accepts `requests` (default, `SERIALIZE_REQUESTS`), `all_requests` / `all-requests`, or `connections`.

The `.thread_model` callback returns the configured model without consulting `next_thread_model`, relying on nbdkit's runtime thread-model reduction. There is no per-connection state and no I/O callback interception.

The behavioral impact is global concurrency reduction for the filter stack. This is useful for unsafe plugins or filters, but can sharply reduce throughput if set more restrictively than necessary.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/noparallel/noparallel.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nozero/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/nozero/Makefile.am

This Automake fragment builds `nbdkit-nozero-filter.la` from `nozero.c`, distributes `nbdkit-nozero-filter.pod`, and conditionally generates its man page. It uses the core nbdkit include paths and standard filter module/link flags.

No common helper library is linked beyond the platform import library. The build contract is aligned with the filter's purpose as a capability and flag-shaping wrapper for zero operations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nozero/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/nozero/nozero.c -->
# File Research: sources/virtualization/nbdkit/filters/nozero/nozero.c

This filter controls advertised and executed write-zeroes behavior. `zero-mode` / `zeromode` accepts `none` (default), `emulate`, `notrim`, and `plugin`; `fast-zero-mode` / `fastzeromode` accepts `default`, `none`, `slow`, and `ignore`.

`.prepare` validates modes that require backend zero support (`notrim` and `plugin`) unless the connection is readonly. `.can_zero` advertises no zero support, nbdkit emulation, or the backend's capability depending on mode. `.can_fast_zero` either delegates to the backend in default plugin modes or reflects the local fast-zero policy.

The `.zero` handler is reached only when zero operations are delegated to the backend. It may reject fast-zero with `ENOTSUP`, silently clear the fast-zero flag, or remove `MAY_TRIM` for `notrim`, then calls `next->zero`.

Edge cases are centered on capability consistency: `zero-mode=plugin` requires backend support, `zero-mode=none` suppresses zero requests, and `fast-zero-mode=ignore` intentionally turns a requested fast zero into a potentially slow zero.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/nozero/nozero.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/offset/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/offset/Makefile.am

This fragment builds `nbdkit-offset-filter.la` from `offset.c`, distributes its POD, and optionally generates the man page. It includes core nbdkit headers plus `common/utils`, then links `libutils.la`, compatibility replacements, and the platform import library.

The module uses the standard filter link flags and optional linker script. Its helper dependency supports parsing/cleanup utilities used by the offset implementation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/offset/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/offset/offset.c -->
# File Research: sources/virtualization/nbdkit/filters/offset/offset.c

This filter exposes a byte subrange of the underlying plugin. Configuration parses `offset=OFFSET` and optional `range=LENGTH` through `nbdkit_parse_size`.

`.get_size` validates that `offset` and `range` lie within the backend size and returns either the configured range or the remaining backend size after the offset. Read, write, trim, zero, and cache callbacks simply add the configured offset before forwarding to `next`.

The extents handler allocates a temporary extents list over the backend coordinate range, delegates to `next->extents`, subtracts the configured offset from each returned extent, and adds translated extents to the caller's list.

Main correctness concerns are integer-boundary checks in `get_size` and extent end calculation when `range` is unset; the filter relies on nbdkit bounds checking for individual requests once the advertised size is correct.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/offset/offset.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/openonce/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/openonce/Makefile.am

This Automake file builds `nbdkit-openonce-filter.la` from `openonce.c`, distributes its POD, and conditionally generates the man page. It uses nbdkit include paths plus `common/utils`, and links utilities, replacements, and the platform import library.

The file enables standard filter module semantics and optional linker-script export filtering. Its linked helpers support cleanup/vector usage in the implementation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/openonce/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/openonce/openonce.c -->
# File Research: sources/virtualization/nbdkit/filters/openonce/openonce.c

This filter opens the underlying plugin once per `(readonly, is_tls, exportname)` tuple, then reuses the same `nbdkit_next` context across multiple client connections. A global vector of `export_entry` records is protected by `export_list_lock`.

`.open` searches for an existing matching context; if absent, it duplicates the export name, calls `nbdkit_next_context_open(..., shared=1)`, prepares the new context, and appends it to the global list. Per-client handles only store the selected shared `next` pointer. `.cleanup` finalizes and closes all retained contexts at server shutdown, noting that finalize failure could imply data loss.

Because requests from different clients can now hit a shared backend context, `.thread_model` upgrades `SERIALIZE_REQUESTS` to `SERIALIZE_ALL_REQUESTS`. All capability, metadata, I/O, extent, and cache callbacks delegate to the handle's stored `h->next` rather than the callback's `next` argument.

The key tradeoff is connection lifetime: contexts remain open even after the last client disconnects. The code comments identify possible future close-on-unused behavior, but the current design favors persistent backend state over resource reclamation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/openonce/openonce.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/partition/Makefile.am

This build fragment compiles the partition filter from `partition.c`, `partition.h`, `partition-gpt.c`, and `partition-mbr.c`. It includes `common/gpt`, core includes, and `common/utils`, and links utility/replacement libraries plus the platform import library.

It distributes `nbdkit-partition-filter.pod` and conditionally builds the man page. Build dependencies reflect that the implementation parses both MBR and GPT partition tables and uses shared endian/GPT structures.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition-gpt.c -->
# File Research: sources/virtualization/nbdkit/filters/partition/partition-gpt.c

This file locates a selected GPT partition. It reads values from the GPT header using little-endian conversion, validates that partition entries start at LBA 2, then scans the partition-entry array for the non-empty entry matching global `partnum`.

`find_gpt_partition` validates the requested partition number against `nr_partition_entries`, enforces entry sizes between 128 bytes and one sector with exact sector divisibility, and checks that the disk can contain primary and backup partition arrays plus GPT overhead. It reads partition-entry sectors as needed and computes `offset` and `range` from `first_lba` and `last_lba` multiplied by global `sector_size`.

The implementation is intentionally conservative: it rejects non-standard GPT layouts where entries are not adjacent to the header and does not perform full GPT CRC/header validation. It depends on `partition.c` for final disk-boundary validation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition-gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition-mbr.c -->
# File Research: sources/virtualization/nbdkit/filters/partition/partition-mbr.c

This file locates primary and logical MBR partitions. It decodes the four-byte little-endian start-sector and sector-count fields from partition table entries and treats type bytes `0x05`, `0x0f`, and `0x85` as extended partitions.

For primary partitions `1..4`, `find_mbr_partition` returns the first matching non-empty, non-extended entry and rejects GPT protective type `0xEE` with guidance about possible sector-size mismatch. For logical partitions, it finds the enclosing extended partition, follows the EBR chain starting at partition number 5, reads each EBR sector, validates alignment and bounds, rejects non-increasing EBR links, and ensures logical partitions stay within the extended partition extent.

Risk controls are stronger for EBR chains than for primary MBR metadata: malformed chains are rejected when they point outside the disk, point to the MBR, loop backward, or describe partitions outside the enclosing extended partition. The code intentionally does not accept unusual valid tables with reverse-ordered EBR chains.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition-mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition.c -->
# File Research: sources/virtualization/nbdkit/filters/partition/partition.c

This is the main partition filter that exposes one selected MBR or GPT partition as a virtual disk. It parses required `partition=<PART>` and optional `partition-sectorsize=<512|4096>`, storing global `partnum` and `sector_size`.

`.config_complete` requires a nonzero partition number. `.open` creates a per-connection handle whose `offset`, `range`, and type are filled by `.prepare`. If sector size was not configured, `.prepare` asks the backend for block size and uses 512 or 4096 when the minimum block size matches, otherwise defaults to 512. It validates disk size, reads LBA 0 and 1, chooses GPT if LBA 1 contains `EFI PART` and the disk is large enough, otherwise chooses MBR by boot signature, then calls the helper parser and verifies the resulting partition lies within the disk.

The filter reports an export description including partition number and table type, returns partition `range` as size, and forwards read/write/trim/zero/cache operations with `h->offset` added. Extents are fetched in backend coordinates and translated back to partition-relative offsets.

Notable edge cases include a typo in the invalid sector-size error message (`4086` instead of `4096`), conservative GPT layout requirements in the helper, and reliance on the advertised partition size to keep later I/O bounded.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition.h -->
# File Research: sources/virtualization/nbdkit/filters/partition/partition.h

This internal header defines sector-size constants (`512`, `4096`, default `512`), declares global `partnum` and `sector_size`, and exposes the MBR/GPT helper entry points used by `partition.c`.

It includes the nbdkit filter API because the helper signatures take `nbdkit_next *` for backend reads. The header is limited to the partition filter module and has no public API role outside this filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/partition/partition.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/pause/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/pause/Makefile.am

This build file compiles `nbdkit-pause-filter.la` from `pause.c` only on non-Windows platforms because the implementation relies on Unix domain sockets. It includes core headers and `common/utils`, links `libutils.la`, and optionally builds the POD-derived manual.

The conditional `if !IS_WINDOWS` is the key build gate. The filter's runtime dependency on Unix socket path limits and POSIX socket APIs is reflected directly in the build rules.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/pause/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/pause/pause.c -->
# File Research: sources/virtualization/nbdkit/filters/pause/pause.c

This filter provides a Unix-domain control socket that can pause and resume NBD request processing. Configuration requires `pause-control=SOCKET`, converted to an absolute path; `.config_complete` validates the socket path length, unlinks stale paths, creates/binds/listens on the socket, and starts the backend config-complete chain.

After fork, a background thread accepts one control connection at a time and reads single-byte commands: `p` pauses, `r` resumes, whitespace is ignored, and unknown commands respond with `X`. Responses are uppercase acknowledgements. Pause is implemented by locking a global `paused` mutex and then waiting on a separate request counter condition variable until all in-flight requests complete. Resume clears the paused state and unlocks the mutex.

Each request wrapper calls `begin_request`, delegates to the backend, and calls `end_request`. Wrapped operations include pread, pwrite, zero, trim, extents, and cache. `begin_request` first passes through the paused mutex and then increments `count_requests`; `end_request` decrements and signals waiters.

Correctness depends on balanced begin/end calls. Since the wrappers do not use cleanup guards, any future early return between begin and end would deadlock pause accounting. Current implementations delegate once and always call `end_request` after the delegate returns.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/pause/pause.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/protect/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/protect/Makefile.am

This fragment builds `nbdkit-protect-filter.la` from `protect.c`, distributes its POD, and optionally generates the manual. It includes the core headers plus `common/regions`, `common/replacements`, and `common/utils`.

The module links `libregions.la`, `libutils.la`, compatibility replacements, and the platform import library. Those dependencies match the implementation's range/region conversion and compatibility helper usage.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/protect/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/protect/protect.c -->
# File Research: sources/virtualization/nbdkit/filters/protect/protect.c

This filter prevents modifications to configured byte ranges unless the requested write would leave protected bytes unchanged. `protect=START-END` adds a protected inclusive range; `protect=~START-END` protects everything except the specified range by adding up to two complementary ranges. Empty starts and ends mean beginning of file and `INT64_MAX`.

During config completion, ranges are sorted and adjacent/overlapping ranges are merged, then converted into a complete `regions` table spanning the 64-bit address space with protected and unprotected regions. Protected regions carry non-NULL data in the region union; unprotected regions do not.

`check_write` walks the affected regions for a write-like request. For protected spans it reads the current backend bytes and compares them to the proposed write buffer, or checks that the current bytes are already zero for trim/zero operations. If the request would alter protected data, it fails with `EPERM`; otherwise the write, trim, or zero is forwarded.

The design allows idempotent writes and zero/trim over already-zero protected data. Its cost is read-before-write overhead on protected regions. Pointer arithmetic on `buf` advances even when `buf == NULL`; this is tolerated by the compiler in this code path but is a portability-sensitive C idiom.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/protect/protect.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/qcow2dec/Makefile.am

This build file compiles the read-only qcow2 decoder filter from `qcow2dec.c` and `qcow2.h`. It includes core headers, replacements, and utilities, and adds zlib, zlib-ng, and libzstd compiler/linker flags when configured.

The module links utilities, replacements, platform import support, and compression libraries. It distributes and optionally generates the `nbdkit-qcow2dec-filter` manual, and uses standard filter module flags plus optional linker-script restriction.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/qcow2.h -->
# File Research: sources/virtualization/nbdkit/filters/qcow2dec/qcow2.h

This internal header defines the packed qcow2 header layout used by `qcow2dec.c`, including v2 fields, v3 feature fields, and `compression_type`. It also defines the qcow2 magic string and bit numbers for known incompatible, compatible, and autoclear feature flags.

The header provides masks for validating/extracting L1 and L2 entries, including reserved-bit masks, offset masks, and the L2 compressed-cluster type bit. It is intentionally narrow and models only the qcow2 metadata needed by the decoder filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/qcow2.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/qcow2dec.c -->
# File Research: sources/virtualization/nbdkit/filters/qcow2dec/qcow2dec.c

This filter exposes a qcow2 file provided by the underlying plugin as a read-only virtual disk. It advertises no write support, emulated cache support, multi-conn consistency, and extents support. `dump_plugin` reports deflate and zstd support according to build-time compression libraries.

`.prepare` is serialized by a global mutex and loads qcow2 metadata once. `get_qcow2_metadata` validates the backend file size, reads and byte-swaps the qcow2 header, checks magic/version, rejects backing files, encryption, snapshots, unsupported incompatible features, invalid cluster sizes, and oversized or out-of-bounds L1 tables. Version 2 files get default v3-like fields. The L1 table is loaded and byte-swapped; L2 table descriptors are allocated lazily, one mutex per L1 entry.

Reads are cluster-based. `qcow2dec_pread` handles unaligned heads/tails through a temporary cluster buffer and aligned bodies directly. `read_l2_entry` maps virtual offsets through L1/L2 indexes, validates reserved bits and L2 table offsets, lazily reads and byte-swaps L2 table clusters under per-table locks, and returns unallocated state. `read_cluster` returns zeroes for missing/zero clusters, reads ordinary allocated clusters from the qcow2 file, or dispatches compressed clusters.

Compressed cluster handling decodes qcow2 compressed L2 fields into host file offset and sector count, bounds-checks reads, caps compressed allocation to twice the cluster size, and decompresses with raw deflate or zstd when available. Unsupported compression libraries are reported once through static atomic flags.

`qcow2dec_extents` rounds the query to cluster boundaries and emits hole/zero extents for unallocated or explicit-zero clusters, allocated extents for compressed and ordinary data clusters, and honors `REQ_ONE`. Major limitations are explicit and enforced: no backing files, no encryption, no internal snapshots, no external data files or extended L2, and no metadata refresh if the qcow2 file size changes after preparation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/qcow2dec/qcow2dec.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/rate/Makefile.am

This fragment builds `nbdkit-rate-filter.la` from `bucket.c`, `bucket.h`, and `rate.c`. It includes core headers, replacements, and utilities, and links utility/replacement libraries plus the platform import library.

The POD manual is distributed and optionally generated. The build split reflects a reusable token-bucket implementation separated from the nbdkit filter wrapper.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/bucket.c -->
# File Research: sources/virtualization/nbdkit/filters/rate/bucket.c

This file implements the token bucket used by the rate filter. Buckets track a fill `rate`, burst `capacity_secs`, token `capacity`, current `level`, and the last update timestamp.

`bucket_init` sets capacity as `rate * capacity_secs`, starts the bucket full, and stores the current time. `bucket_adjust_rate` changes the fill rate and capacity while clamping the current level. `bucket_run` refills based on elapsed microseconds, deducts requested tokens if available, or empties the bucket and returns how many tokens remain unavailable along with an estimated sleep time.

`rate == 0` is the no-limit case and immediately returns no required sleep. Timing uses `gettimeofday`, so negative elapsed time from non-monotonic clock changes is clamped to zero. Debug logging is controlled by `-D rate.bucket=1`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/bucket.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/bucket.h -->
# File Research: sources/virtualization/nbdkit/filters/rate/bucket.h

This header declares `struct bucket` and the token-bucket API used by `rate.c`: `bucket_init`, `bucket_adjust_rate`, and `bucket_run`. Comments document that capacity is expressed in rate-equivalent seconds and that callers must retry `bucket_run` after sleeping because another thread may consume replenished tokens first.

The API is deliberately stateful and synchronization-free; callers are responsible for locking around bucket access, which `rate.c` does with per-bucket mutexes.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/bucket.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/rate.c -->
# File Research: sources/virtualization/nbdkit/filters/rate/rate.c

This filter rate-limits read and write bandwidth with global and per-connection token buckets. Configuration supports `rate`, `connection-rate`, dynamic `rate-file`, dynamic `connection-rate-file`, and `burstiness` in seconds.

`.get_ready` initializes global read/write buckets. `.open` initializes per-connection read/write buckets and mutexes. `maybe_adjust` optionally reads the first line of a configured rate file, parses a size value, and updates a bucket under lock. `maybe_sleep` converts byte counts to bits, runs a bucket under lock, and sleeps with `nbdkit_nanosleep` until enough tokens can be obtained.

`rate_pread` applies dynamic global-read adjustment, global read limiting, dynamic per-connection read adjustment, and per-connection read limiting before forwarding. `rate_pwrite` mirrors this for writes. Reads and writes have separate buckets, so the configured limit is enforced independently in each direction.

Operational risks are expected for sleep-based throttling: dynamic rate files are polled per request, system clock jumps can affect refill calculations, and rate units are bits per second derived from byte counts times eight without transport overhead.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rate/rate.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/readahead/Makefile.am

This build fragment compiles the readahead filter from `readahead.c`, `readahead.h`, and `bgthread.c`, includes core headers and `common/utils`, and links utility/replacement libraries plus platform import support.

It distributes and optionally generates the POD manual. The source split separates the filter request logic from the background-thread command consumer.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/bgthread.c -->
# File Research: sources/virtualization/nbdkit/filters/readahead/bgthread.c

This file implements the per-connection readahead background thread. The thread waits on a condition variable until commands are present, removes the first queued command, and handles `CMD_QUIT` or `CMD_CACHE`.

`CMD_CACHE` invokes the underlying plugin's `.cache` callback for the queued offset/count and ignores errors because readahead is advisory and there is no client response path. `CMD_QUIT` exits the thread after all earlier queued commands have been processed.

The command queue is protected by the control mutex. The thread assumes command construction and `next` lifetime are managed by `readahead.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/bgthread.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/readahead.c -->
# File Research: sources/virtualization/nbdkit/filters/readahead/readahead.c

This filter issues asynchronous cache hints after sequential reads. It maintains a global adaptive window between 32 KiB and 4 MiB, plus global `last_offset` and `last_readahead` guarded by `window_lock`. It records the final server thread model in `.get_ready`.

Each connection creates a background thread and command queue in `.open`, then sends a quit command and joins the thread in `.close`. The filter only works when the underlying stack advertises `NBDKIT_CACHE_NATIVE` and the final thread model is `PARALLEL`; otherwise `.can_cache` logs a warning and may suggest adding the cache filter.

On `.pread`, if working, it computes a cache command starting immediately after the synchronous read, clips it to backend size, adapts the window based on forward progress, queues the command for the background thread, and then performs the actual synchronous read. The asynchronous `.cache` request is best-effort and not reported to the client.

The main correctness dependency is thread-model compatibility: the background thread calls into `next->cache` concurrently with normal reads, so the filter refuses to be useful unless the final stack is parallel-safe and cache-native.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/readahead.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/readahead.h -->
# File Research: sources/virtualization/nbdkit/filters/readahead/readahead.h

This internal header defines the background command queue shared by `readahead.c` and `bgthread.c`. Commands are either `CMD_QUIT` or `CMD_CACHE` and include the target `nbdkit_next`, offset, and count for cache requests.

It defines `struct bgthread_ctrl` with a vector-backed command queue, mutex, and condition variable, and declares `readahead_thread`. The header owns no policy; it only shares queue and thread-control types.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readahead/readahead.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readonly/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/readonly/Makefile.am

This fragment builds `nbdkit-readonly-filter.la` from `readonly.c`, includes core headers and `common/utils`, and links utilities, replacements, and platform import support. It distributes and optionally builds the manual.

The build dependencies are modest; the implementation primarily uses the nbdkit filter API and POSIX `access`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readonly/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/readonly/readonly.c -->
# File Research: sources/virtualization/nbdkit/filters/readonly/readonly.c

This filter forces permanent or file-controlled read-only behavior. Without `readonly-file`, `.open` forces the underlying plugin to open readonly and `.can_write` returns false. With `readonly-file=FILENAME`, the backend is opened normally, `.can_write` delegates, and mutating requests are rejected whenever the file is readable at request time.

`is_readonly_mode` centralizes rejection for pwrite, trim, and zero, logging the operation and returning `EROFS`. Flush is intentionally not blocked because writes issued before read-only mode may still need to be persisted.

This design supports dynamic read-only toggling by creating/removing the configured file. The tradeoff is that advertised write capability can remain true while individual write-like requests later fail with `EROFS`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/readonly/readonly.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/retry-request/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/retry-request/Makefile.am

This build file compiles `nbdkit-retry-request-filter.la` from `retry-request.c`, includes core headers and `common/utils`, and links utility/replacement libraries plus platform import support. It distributes and optionally builds the filter manual.

The module implements per-request retry without reopening the backend, so its build dependencies are lighter than the full reconnecting retry filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/retry-request/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/retry-request/retry-request.c -->
# File Research: sources/virtualization/nbdkit/filters/retry-request/retry-request.c

This filter retries failed individual backend calls without reopening the backend connection. Configuration supports `retry-request-retries` (default 2, capped at 1000), `retry-request-delay`, and `retry-request-open=false`.

The `RETRY_START` / `RETRY_END` macros wrap each operation, sleeping before retries and preserving/setting errno on interrupted sleeps. `.open` can retry the initial next-open call; `.get_size`, pread, pwrite, trim, flush, zero, extents, and cache are all retried with the same backend context.

The extents handler recreates a temporary extents object for each retry and copies successful extents back to the caller, avoiding partial extent accumulation across failed attempts.

This filter is appropriate for transient request failures where the connection remains usable. It is not a reconnect/reopen filter; persistent connection failures require the separate `retry` filter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/retry-request/retry-request.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/retry/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/retry/Makefile.am

This fragment builds `nbdkit-retry-filter.la` from `retry.c`, includes core headers and `common/utils`, and links utility/replacement libraries plus platform import support. It distributes and optionally builds the manual.

Unlike `retry-request`, this filter needs backend context reopen support, but the build-time dependencies remain within the nbdkit filter API and common utilities.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/retry/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/retry/retry.c -->
# File Research: sources/virtualization/nbdkit/filters/retry/retry.c

This filter retries failed operations by closing and reopening the backend context. Configuration includes `retries` (default 5), `retry-delay`, `retry-exponential`, and `retry-readonly` to force reopened contexts to readonly after failure.

Because `nbdkit_backend_reopen` is not safe against another request on the same connection, `.thread_model` reduces concurrency to `SERIALIZE_REQUESTS`. Each handle stores the original readonly flag, export name, nbdkit context, reopen count, and whether a backend is currently open.

`do_retry` implements retry state: it sleeps, optionally doubles delay, finalizes/closes the old `next`, clears the context's next pointer, opens a fresh backend context with original-or-forced-readonly mode, prepares it, installs it into the context, and tells the caller to retry the data operation. Open itself uses the same logic if the initial next-open fails.

Data callbacks validate request ranges against current size, check backend capabilities before write-like and advisory operations, handle FUA/fast-zero constraints, and retry on failure. Extents are built in a temporary object per attempt and copied back after success. With `retry-readonly`, write/trim/zero requests after a reopen fail with `EROFS`.

The filter can recover from broken backend connections, but it changes connection identity under the client. Operations that are not idempotent, or backends whose state changes between reconnects, require careful deployment.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/retry/retry.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rotational/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/rotational/Makefile.am

This build file compiles `nbdkit-rotational-filter.la` from `rotational.c`, includes core/generated headers, and uses the standard filter module flags with optional linker-script support. It distributes and optionally generates the manual.

The implementation has no common helper dependencies beyond platform import support.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rotational/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/rotational/rotational.c -->
# File Research: sources/virtualization/nbdkit/filters/rotational/rotational.c

This filter overrides the advertised rotational property. The `rotational=true|false` parameter is parsed as a boolean and defaults to true.

`.is_rotational` returns the configured value without delegating to the backend. The filter has no per-connection state and does not alter I/O behavior; it only shapes metadata that clients may use for scheduling or heuristics.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/rotational/rotational.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/scan/Makefile.am

This fragment builds `nbdkit-scan-filter.la` from `scan.c`, `scan.h`, and `bgthread.c`, includes core headers and `common/utils`, and links utilities/replacements plus platform import support. It distributes and optionally builds the manual.

Only `bgthread.c` is in this work item; `scan.c` and `scan.h` belong to the next group, but this Makefile establishes the full module composition and dependencies.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/bgthread.c -->
# File Research: sources/virtualization/nbdkit/filters/scan/bgthread.c

This file implements the scan filter's background cache-scanning thread. It maintains a global scan clock guarded by `clock_lock`; helper functions advance, reset, or read the starting offset depending on `scan_clock`.

`scan_thread` obtains the backend size, then loops from the current starting offset to the end in `scan_size` chunks. On each iteration it drains queued commands under the control lock: `CMD_QUIT` exits, while `CMD_NOTIFY_PREAD` can jump the scan offset forward to a recently read position. It updates the global clock and issues `next->cache` for the current chunk, ignoring cache errors because scanning is advisory.

If `scan_forever` is enabled, the thread resets the clock and starts over after reaching the end; otherwise it logs completion and exits. The file depends on globals and command types declared in `scan.h`, which is outside this group.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/bgthread.c -->