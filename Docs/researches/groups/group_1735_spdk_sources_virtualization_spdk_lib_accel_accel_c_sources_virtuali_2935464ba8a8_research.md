# Group Research: group_1735_spdk_sources_virtualization_spdk_lib_accel_accel_c_sources_virtuali_2935464ba8a8

Scope checked against `Docs/research_subset_a.md`: the subset includes `sources/virtualization/spdk`, so every file in this group is in scope. I read each listed file completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel.c -->
# File Research: sources/virtualization/spdk/lib/accel/accel.c

`accel.c` is the core SPDK accelerator framework implementation. It owns global module registration and opcode assignment, per-channel task/sequence/buffer pools, sequence execution, memory-domain bounce-buffer handling, crypto-key lifecycle, framework initialization/finalization, config JSON dumping, driver selection, options, and stats.

Major public submission APIs build `spdk_accel_task` objects for copy, dualcast, compare, fill, CRC32C, copy+CRC32C, compress/decompress, encrypt/decrypt, XOR, DIF, and DIX operations. Single-shot submissions allocate a task from the channel pool, populate source/destination iovecs, opcode-specific fields, domains, and completion callback, then dispatch through the selected module for that opcode.

The sequence API lets callers append operations to a `spdk_accel_sequence`. Appended operations carry memory-domain metadata, optional per-step callbacks, and are later executed by `spdk_accel_sequence_finish()`. Before execution, the framework attempts copy-elision/merge optimizations so adjacent copy operations can be folded into neighboring operations when iovec and domain relationships allow it.

The sequence state machine is a central design point. It moves through virtual accel-buffer allocation, bounce-buffer allocation, memory-domain pull/push operations, module task execution, driver execution, per-task completion, error handling, and final sequence completion. It prevents recursive processing with `in_process_sequence`, and completion paths re-enter the state machine only after state changes.

Memory-domain support is handled in two layers. The accel framework exposes its own accel memory domain where buffers are represented by a sentinel pointer plus an `accel_buffer` domain context. It also adapts operations for modules that do not support foreign memory domains by allocating iobuf-backed bounce buffers, pulling source data into them, and pushing destination data back after task completion.

The crypto-key path validates key creation parameters, cipher strings, tweak-mode strings, module crypto support, AES-XTS second-key requirements, key-size equality, and identical XTS keys with timing-side-channel-aware comparison. Key material is scrubbed before free, key objects are kept in a spinlock-protected keyring, and module-specific key init/deinit hooks own hardware/software private state.

Initialization registers the accel io_device, creates the accel memory domain, initializes modules, optionally initializes an accel driver, assigns opcodes by module priority plus user overrides, validates paired encrypt/decrypt and compress/decompress module choices, initializes opcode memory-domain support flags, and registers the iobuf module. Finalization unregisters the io_device, destroys crypto keys, frees opcode overrides, finishes modules, destroys spinlocks, and destroys the memory domain.

Stats are tracked per channel and folded into global stats when channels are destroyed. `accel_get_stats()` aggregates global retired-channel stats plus all live channel stats asynchronously. Opcode-specific counters track executed, failed, and byte counts; retry counters cover task, sequence, iobuf, and buffer-descriptor pressure.

Important dependencies include `spdk/accel_module.h`, `spdk/thread.h`, `spdk/dma.h`, `spdk/iobuf`, memory domains, JSON config writers, `spdk/hexlify.h`, and SPDK spinlocks. The file assumes all opcodes ultimately have a module, with the software module providing fallback coverage.

Research notes: resource sizing is governed by `spdk_accel_opts`, and `task_count` must stay at or above the in-sequence deadlock-avoidance limit. The framework uses assertions for several internal invariants, especially aux-data pool availability and state transitions, so integration mistakes tend to fail hard in debug builds.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_internal.h -->
# File Research: sources/virtualization/spdk/lib/accel/accel_internal.h

`accel_internal.h` is the private header shared by accel core, RPC, and software-module code. It includes public accel/module headers, queue utilities, and config state.

It defines `ACCEL_AES_XTS`, the internal `module_info` structure used to report a module name and supported opcodes, `accel_operation_stats`, and `accel_stats`. The stats structure mirrors what the RPC layer exposes: per-op executed/failed/bytes, sequence counts, outstanding counts, and retry counters.

The header declares `_accel_for_each_module()`, crypto string conversion helpers, JSON dump helpers for crypto-key parameters and key lists, and `accel_get_stats()`. These are intentionally internal and support the RPC/control-plane files without exposing implementation details through public headers.

Research notes: this file is small but forms the internal ABI between `accel.c` and `accel_rpc.c`; changes to `accel_stats` or crypto dump helpers must be kept in sync with the RPC response shape.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_rpc.c -->
# File Research: sources/virtualization/spdk/lib/accel/accel_rpc.c

`accel_rpc.c` implements JSON-RPC control-plane methods for the accel framework. It is runtime/startup glue over the core APIs in `accel.c` and the internal helpers from `accel_internal.h`.

Registered RPCs include `accel_get_opc_assignments`, `accel_get_module_info`, `accel_assign_opc`, `accel_crypto_key_create`, `accel_crypto_keys_get`, `accel_crypto_key_destroy`, `accel_set_driver`, `accel_set_options`, and `accel_get_stats`.

Opcode assignment RPCs translate between opcode strings and enum values, validate requested operation names, and call `spdk_accel_assign_opc()`. Assignment is startup-only, matching the framework restriction that opcode-to-module overrides must be set before modules start.

Crypto-key RPCs decode cipher, key, optional key2, optional tweak mode, and key name. They translate decoded enum values back to framework strings and call `spdk_accel_crypto_key_create()`. Sensitive key strings decoded from RPC are explicitly scrubbed with `spdk_memset_s()` before freeing. Key listing can dump one key by name or all keys; destruction resolves the key object then calls the framework destroy routine.

Driver and option RPCs call `spdk_accel_set_driver()` and `spdk_accel_set_opts()`. Option decoding avoids direct packed-struct decode by copying into an RPC-specific context first, then back into `spdk_accel_opts`.

Stats RPC aggregation is asynchronous. `accel_get_stats()` supplies an `accel_stats` snapshot, and the RPC writer emits sequence counters, outstanding task counters, retry counters, and only operation entries that have executed or failed counts. Each operation entry includes opcode name, assigned module name, executed, failed, and byte totals.

Research notes: error responses use SPDK JSON-RPC error codes for parse/invalid-param failures and `spdk_strerror()` for framework return codes. The file is strictly control plane; no datapath operations are issued here.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_sw.c -->
# File Research: sources/virtualization/spdk/lib/accel/accel_sw.c

`accel_sw.c` implements the built-in software accelerator module. It registers an accel module named `software` with fallback support for all framework opcodes: copy, fill, dualcast, compare, CRC32C, copy+CRC32C, compression/decompression, encryption/decryption, XOR, DIF, and DIX.

The module uses per-channel state for optional ISA-L deflate/inflate state, optional LZ4 streams, a completion poller, and a queue of tasks pending completion. Operations execute synchronously inside `sw_accel_submit_tasks()`, but completions are queued to a poller so callbacks are not invoked inline with submission.

Basic memory operations are straightforward: copy uses `spdk_ioviter`, compare walks paired iovecs and returns `-EILSEQ` on mismatch, fill requires a single destination iovec, dualcast requires single source and two single destinations, CRC32C uses SPDK CRC helpers, and XOR uses `spdk_xor_gen()`.

Compression supports DEFLATE via ISA-L when `SPDK_CONFIG_ISAL` is enabled and LZ4 when `SPDK_CONFIG_HAVE_LZ4` is enabled. The software module advertises supported algorithms based on build flags and exposes compression level ranges. Without the required libraries, relevant operations return errors rather than silently doing nothing.

AES-XTS crypto support depends on `SPDK_CONFIG_ISAL_CRYPTO`. Key initialization installs function pointers for 128-bit or 256-bit XTS encrypt/decrypt routines. Runtime crypto walks source and destination iovec lists, processes data in logical block-sized units, increments the IV after each full block, supports in-place operation when no destination iovs are present, and enforces equal source/destination total length and block-size alignment.

DIF/DIX operations delegate to SPDK DIF helpers: verify, verify-copy, generate, generate-copy, DIX generate, and DIX verify. The software module reports no buffer alignment requirement through `get_operation_info()`.

Research notes: this file is the guarantee that the accel framework can assign every opcode even without hardware modules. Build-flag conditionals are important for feature availability: an opcode may be supported in the generic sense while a specific compression algorithm or crypto implementation returns `-EINVAL` or `-ENOTSUP` if its library support is absent.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/accel/accel_sw.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/Makefile -->
# File Research: sources/virtualization/spdk/lib/ae4dma/Makefile

This Makefile builds the SPDK `ae4dma` library from `ae4dma.c`. It sets `SPDK_ROOT_DIR`, includes the common SPDK make rules, declares shared-object version `2.0`, sets `LIBNAME = ae4dma`, and uses `spdk_ae4dma.map` as the symbol map.

Research notes: this is a minimal library build file. The implementation surface for the library is contained in `ae4dma.c` plus the internal/spec headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma.c -->
# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma.c

`ae4dma.c` implements the AMD AE4DMA PCI DMA-engine library. It handles device enumeration, attach/detach, PCI BAR mapping, queue setup, descriptor preparation, submission doorbells, and completion polling.

The global driver state is protected by a pthread mutex and tracks attached AE4DMA channels in a TAILQ. `spdk_ae4dma_probe()` enumerates PCI devices through `spdk_pci_ae4dma_get_driver()`, skips devices already attached, runs the caller probe callback, attaches accepted devices, inserts them into the global list, and invokes the attach callback.

Attach enables PCI bus mastering, allocates a channel object, maps BAR0, configures hardware queue count, sets copy capability, initializes up to `AE4DMA_MAX_HW_QUEUES`, allocates DMA descriptor rings with `spdk_dma_zmalloc()`, translates descriptor-ring virtual addresses to physical addresses, programs queue registers, enables queues, disables interrupts, and allocates callback-ring metadata.

Copy submission is built in `spdk_ae4dma_build_copy()`. It walks source and destination iovec pairs with `spdk_ioviter`, translates each segment with `spdk_vtophys()`, splits work where physical contiguity differs between source and destination, checks descriptor-ring headroom, writes AE4DMA descriptors, and attaches the user callback only to the final descriptor in the batch.

`spdk_ae4dma_flush()` updates the hardware write index for a queue. Event processing reads descriptor status from the command queue tail, stops when it reaches a submitted descriptor, reports descriptor error codes, decrements pending descriptor count, invokes descriptor callbacks, and advances the software tail.

Detach removes the channel from the global attached list, unmaps the PCI BAR, frees each queue’s DMA descriptor memory and callback ring, and frees the channel object.

Research notes: the implementation reserves four descriptors of ring headroom before declaring a ring full. Error handling during queue startup can return after partial allocation; callers rely on destruct cleanup, so cleanup coverage for partially initialized queues is important when modifying this code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma_internal.h -->
# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma_internal.h

`ae4dma_internal.h` defines private AE4DMA helper macros and in-memory channel/queue structures. It includes the public AE4DMA API, spec definitions, SPDK queue macros, and MMIO helpers.

It provides `upper_32_bits()` and `lower_32_bits()` helpers, descriptor-ring sizing constants, callback metadata structure `ae4dma_descriptor`, command queue structure `ae4dma_cmd_queue`, and private channel structure `spdk_ae4dma_chan`.

Each command queue tracks MMIO queue registers, DMA-visible descriptor base, callback ring, software tail, queue size, physical ring address, write index, and pending descriptor count. Each channel tracks the PCI device, max transfer size, BAR-mapped register base, fixed array of hardware queues, queue count, DMA capability flags, and global attached-list linkage.

Inline helpers report command-queue fullness and validate requested queue count against `AE4DMA_MAX_HW_QUEUES`.

Research notes: this header’s structures are used directly by `ae4dma.c`, so layout changes affect queue setup, event processing, and descriptor building.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma_spec.h -->
# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma_spec.h

`ae4dma_spec.h` captures AE4DMA hardware-facing constants, descriptor layout, status values, queue status values, and queue register layout.

It defines 16 hardware queues, 32 descriptors per queue indirectly via the internal header, queue enable bits, common config offset, PCI BAR index, descriptor status enum values, and hardware queue status enum values.

The AE4DMA command descriptor is exactly 32 bytes: control/timestamp dword, status/error/id dword, length, reserved, source low/high, and destination low/high. A static assertion enforces this size.

The per-queue register block includes control, status, max index, read index, write index, interrupt status, and queue-base low/high registers. The register structure is packed/aligned for MMIO access.

Research notes: descriptor field order and register layout are hardware ABI. Any change must match the AE4DMA device specification and the MMIO programming in `ae4dma.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ae4dma/ae4dma_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/Makefile -->
# File Research: sources/virtualization/spdk/lib/bdev/Makefile

This Makefile builds the SPDK `bdev` library. It includes `bdev.c`, `bdev_rpc.c`, `bdev_zone.c`, `part.c`, and `scsi_nvme.c`, and conditionally includes `vtune.c` when `CONFIG_VTUNE` is enabled.

It sets shared-object version `20.0`, `LIBNAME = bdev`, and uses `spdk_bdev.map` as the symbol map.

Research notes: the listed group covers support files in this library but not the main `bdev.c`, which is still part of the build through this Makefile.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_internal.h -->
# File Research: sources/virtualization/spdk/lib/bdev/bdev_internal.h

`bdev_internal.h` is a small private header for bdev library internals. It declares the zero-buffer size constant, forward-declares core bdev types, and exposes internal helpers used by support files.

Declared helpers include obtaining a `spdk_bdev_io` from a channel, initializing and submitting bdev I/O, allocating/freeing I/O stats, and asynchronously resetting device stats. It also declares the reset-stat callback type.

Research notes: `bdev_zone.c` uses these helpers to allocate and submit zone-management I/O. `bdev_rpc.c` uses stat allocation and reset helpers for JSON-RPC I/O-stat endpoints.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_rpc.c -->
# File Research: sources/virtualization/spdk/lib/bdev/bdev_rpc.c

`bdev_rpc.c` implements core SPDK bdev JSON-RPC methods. It is control-plane code for global bdev options, examination, device inventory, I/O statistics, QoS, queue-depth sampling, and histograms.

Registered RPCs include `bdev_set_options`, `bdev_wait_for_examine`, `bdev_examine`, `bdev_get_iostat`, `bdev_reset_iostat`, `bdev_get_bdevs`, `bdev_set_qd_sampling_period`, `bdev_set_qos_limit`, `bdev_enable_histogram`, `bdev_get_histogram`, and `bdev_get_histogram_borders`.

Option setting uses an X-macro field list shared between the generated RPC context and `spdk_bdev_opts`, guarded by a static size assertion. It decodes optional pool/cache/examine/iobuf values and calls `spdk_bdev_set_opts()`.

Examination RPCs either wait for all automatic examine work to complete or trigger examination of a named bdev. Device inventory emits aliases, product name, block geometry, preferred write/unmap hints, UUID, NUMA id, metadata/DIF fields, QoS limits, claim state, zoned fields, supported I/O types, memory-domain types, and driver-specific JSON.

I/O stats handling is asynchronous and reference-counted by outstanding bdev count. It supports all bdevs, selected names, optional per-channel stats for exactly one bdev, and optional reset mode. It opens bdev descriptors, allocates stats buffers, gathers device or per-channel stats, emits JSON, closes descriptors, and frees contexts after all asynchronous callbacks complete.

Reset stats follows similar asynchronous fan-out. It can reset a single named bdev or all bdevs, supports reset mode, calls driver-specific reset hooks when present, and completes the RPC after all device stat reset callbacks return.

QoS and queue-depth RPCs open the named bdev, configure sampling period or rate limits, and return asynchronous completion for QoS. Histogram RPCs enable/disable histogram collection with optional opcode, granularity, min, and max values; readout either returns base64-encoded bucket data plus metadata or counts for requested histogram borders converted from microseconds to ticks.

Research notes: this file is careful about not beginning JSON responses until it knows asynchronous fan-out can be represented correctly. Many error paths close descriptors immediately after submitting asynchronous operations, relying on bdev references held by the operation itself.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_zone.c -->
# File Research: sources/virtualization/spdk/lib/bdev/bdev_zone.c

`bdev_zone.c` implements zoned-block-device helper APIs over the generic bdev I/O path.

Simple getters expose zone size, number of zones, zone-id calculation from an LBA, max zone append size, max open zones, max active zones, and optimal open zones. Zone-id calculation optimizes power-of-two zone sizes with a mask and otherwise uses integer division.

I/O helpers allocate a bdev I/O from the channel, populate zone-management or zone-append fields, initialize callback metadata with `bdev_io_init()`, and submit through `bdev_io_submit()`.

Supported operations are zone info retrieval, zone management action, zone append with optional metadata, vector zone append with optional metadata, and retrieval of append completion location from a completed bdev I/O.

Research notes: this file does not validate zoned capability itself; it assumes upper bdev layers and I/O submission validation enforce whether the target bdev supports the requested zoned operation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/bdev_zone.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/part.c -->
# File Research: sources/virtualization/spdk/lib/bdev/part.c

`part.c` provides common infrastructure for partition-like virtual bdevs backed by a base bdev. It handles base construction, base lifetime, partition construction/destruction, I/O channel creation, I/O remapping, hotremove, and DIF/DIX reference-tag remapping.

A `spdk_bdev_part_base` owns the opened base descriptor, base bdev pointer, refcount, module/fn_table pointers, tailq of partitions, custom channel callbacks, free callback, remove callback, and the thread where the base was opened. Closing the base descriptor is posted back to the opening thread when needed.

Partition destruction unregisters the io_device asynchronously, removes the partition from the base tailq, decrements the base refcount, releases the claimed base bdev when the last partition is gone, completes bdev destruction, and frees partition-owned strings and memory.

The partition I/O table blocks raw NVMe passthrough I/O types because a partition cannot safely decode and remap arbitrary NVMe commands. Other supported I/O types are delegated based on the base bdev’s support.

I/O submission remaps partition-relative offsets by adding `part->internal.offset_blocks`. It handles read, write, write zeroes, unmap, flush, reset, abort, zcopy, compare, compare-and-write, copy, and write-uncorrectable operations. Reads and writes use extended I/O options to preserve memory-domain and metadata pointers.

DIF reference-tag remapping is a key behavior. For writes, it remaps from partition-relative reference tags to base-device reference tags before submission. For reads, completion remaps tags back from base offsets to partition offsets. It supports interleaved metadata via `spdk_dif_remap_ref_tag()` and separate metadata via `spdk_dix_remap_ref_tag()`.

Base construction opens the named base bdev with an event callback, stores module/fn-table/tailq/free/channel callbacks, and records the thread. Partition construction copies base geometry and metadata/DIF properties, assigns name/product, generates a deterministic SHA1 UUID from base UUID plus offset/length unless an explicit UUID is supplied, claims the base bdev on first partition, registers an io_device, registers the child bdev, and inserts it into the base tailq.

Research notes: this is shared infrastructure for many virtual bdev modules. The most sensitive areas are base-claim lifetime, async destructor ordering, thread-affine close handling, and DIF remapping correctness.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/part.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/scsi_nvme.c -->
# File Research: sources/virtualization/spdk/lib/bdev/scsi_nvme.c

`scsi_nvme.c` maps NVMe completion status fields stored in a bdev I/O into SCSI status, sense key, ASC, and ASCQ values.

`spdk_scsi_nvme_translate()` switches first on NVMe status code type: generic, command specific, media error, vendor specific, and default. It then maps known NVMe status codes to SCSI good status, check condition, task aborted, reservation conflict, illegal request, medium error, hardware error, not ready, data protect, or miscompare as appropriate.

Generic mappings cover success, invalid opcode/field, data transfer or capacity errors, power-loss abort, internal device error, request/queue/fused aborts, invalid namespace/format, LBA out of range, namespace not ready, reservation conflict, and many protocol/format cases defaulting to illegal request.

Command-specific mappings cover invalid format, conflicting attributes, attempted write to read-only range, and many admin/namespace/firmware/protection cases defaulting to illegal request.

Media-error mappings distinguish write faults, unrecovered read errors, guard/app/ref tag check failures, compare failure, access denied, and default media-status cases.

Research notes: this function is policy/compatibility glue for SCSI-facing consumers of NVMe-backed bdevs. Updating it requires awareness of both NVMe status codes and SCSI sense conventions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/scsi_nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/bdev/vtune.c -->
# File Research: sources/virtualization/spdk/lib/bdev/vtune.c

`vtune.c` conditionally includes Intel VTune static instrumentation support when `SPDK_CONFIG_VTUNE` is enabled.

It includes `spdk/config.h`, guards the rest of the file with `#if SPDK_CONFIG_VTUNE`, suppresses selected GCC warnings triggered by VTune code, and includes `ittnotify_static.c`.

Research notes: this is an integration wrapper rather than SPDK logic. Build behavior depends entirely on `CONFIG_VTUNE`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/bdev/vtune.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/Makefile -->
# File Research: sources/virtualization/spdk/lib/blob/Makefile

This Makefile builds the SPDK `blob` library from `blobstore.c`, `request.c`, `zeroes.c`, and `blob_bs_dev.c`. It sets shared-object version `14.0`, names the library `blob`, and uses `spdk_blob.map` for symbol exports.

Research notes: the listed group includes only the blob-backed `bs_dev` adapter file from this library, not the main blobstore implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/blob/blob_bs_dev.c -->
# File Research: sources/virtualization/spdk/lib/blob/blob_bs_dev.c

`blob_bs_dev.c` implements a read-only `spdk_bs_dev` adapter backed by an SPDK blob. It is used for blobstore layering cases such as snapshots or copy-on-write backing devices.

Write, writev, writev_ext, write_zeroes, and unmap are hard-fail paths: they invoke the callback with `-EPERM` and assert false. Read paths wrap `spdk_blob_io_read()`, `spdk_blob_io_readv()`, and `spdk_blob_io_readv_ext()` and forward completion through `blob_bs_dev_read_cpl()`.

`zero_trailing_bytes()` handles cases where the requested child blob range extends past the backing blob’s block count. It zeroes the trailing payload bytes and reduces the LBA count before submitting the backing blob read, so reads beyond the backing extent return zero-filled data rather than reading invalid backing ranges.

Destroy closes the backing blob asynchronously and frees the adapter on close completion. Errors during close are logged before freeing.

Copy-on-write helpers expose whether a range is zeroes, whether a range is valid, LBA translation to an allocated blob cluster or backing device, and degraded state. `is_zeroes` and `translate_lba` check whether the blob IO unit is allocated locally; if not, they consult the backing `bs_dev` using translated backing LBAs. `is_range_valid` treats the blob’s active cluster count as the valid range.

`bs_create_blob_bs_dev()` allocates the adapter, sets block count from active clusters and IO units per cluster, sets block size to blobstore IO-unit size, wires read-only operations and COW query callbacks, stores the blob pointer, and returns the embedded `spdk_bs_dev`.

Research notes: this adapter deliberately denies mutation and is intended for backing-device semantics. The trailing-zero loop is important for expanded children over smaller backing blobs; changes there should be audited carefully for multi-iovec zeroing behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/blob/blob_bs_dev.c -->