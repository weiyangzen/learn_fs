# Research: subset-b-001224

Grouped research for ARM CryptoCell ccree hash/request/power/SRAM helpers and Chelsio crypto build wiring. Each section preserves the source path expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.c

## Purpose

`cc_hash.c` implements the ARM CryptoCell asynchronous hash and MAC provider for the Linux crypto API. It registers software-facing `ahash` algorithms backed by CryptoCell descriptors: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SM3, HMAC variants, AES-XCBC, and AES-CMAC when the detected hardware revision and standard-body capability bits permit them.

The file also owns hash-specific SRAM constants. During allocation and resume it copies digest-length constants and larval digests into CryptoCell SRAM so later request descriptors can load hash initial state without embedding all constants in every request.

## Important APIs, Types, And Functions

Key private types are `struct cc_hash_handle`, which tracks SRAM offsets and registered algorithms; `struct cc_hash_alg`, the runtime wrapper around `struct ahash_alg`; `struct cc_hash_ctx`, the per-transform DMA-backed state for digest buffers, HMAC/IPAD/OPAD material, key parameters, hash mode, and hardware mode; and `struct hash_key_req_ctx`, temporary key state for `setkey`.

Main crypto API callbacks are `cc_hash_init`, `cc_hash_update`, `cc_hash_final`, `cc_hash_finup`, `cc_hash_digest`, `cc_hash_setkey`, `cc_hash_export`, and `cc_hash_import`. MAC-specific callbacks are `cc_mac_update`, `cc_mac_final`, `cc_mac_finup`, `cc_mac_digest`, `cc_xcbc_setkey`, and `cc_cmac_setkey`. Registration is driven by `driver_hash[]`, `cc_alloc_hash_alg()`, `cc_hash_alloc()`, and `cc_hash_free()`.

Descriptor helpers include `cc_restore_hash()`, `cc_fin_hmac()`, `cc_fin_result()`, `cc_set_desc()`, `cc_setup_xcbc()`, and `cc_setup_cmac()`. SRAM helpers exported to AEAD/hash code are `cc_init_hash_sram()`, `cc_larval_digest_addr()`, and `cc_digest_len_addr()`.

## Control Flow

On driver allocation, `cc_hash_alloc()` allocates the handle, computes SRAM space based on hardware revision, reserves it with `cc_sram_alloc()`, initializes the SRAM constants through `cc_init_hash_sram()`, then registers each eligible `ahash` algorithm. HMAC-capable templates register a keyed algorithm first, then a plain hash algorithm unless the template is XCBC/CMAC-only.

For normal hashing, `cc_hash_init()` seeds request state from HMAC precomputed state or from larval digests. `cc_hash_update()` maps only block-aligned processable data through `cc_map_hash_request_update()`, restores state into hardware, processes descriptors, and writes intermediate digest and byte-count state back. `cc_hash_final()` and `cc_hash_finup()` call `cc_do_finup()`, restore state, process final data with padding, optionally run the outer HMAC pass, and write the digest result. `cc_hash_digest()` performs one-shot initialization, data processing, optional HMAC finish, and result write in one descriptor sequence.

HMAC `setkey` hashes keys larger than the block size, zero-pads shorter keys, writes the normalized key to the OPAD/IPAD workspace, and then derives and stores the inner and outer starting states. XCBC `setkey` derives K1/K2/K3 by encrypting fixed constants with the AES key. CMAC `setkey` stores the AES key directly, with special 192-bit padding to the hardware's maximum key load size.

## State And Persistence Behavior

Per-transform state lives in `cc_hash_ctx` and is DMA-mapped for the transform lifetime by `cc_alloc_ctx()` and unmapped by `cc_free_ctx()`. Per-request state lives in `struct ahash_req_ctx`, including two partial-block buffers, digest snapshots, digest byte count, MLLI metadata, and DMA addresses. Export/import serializes a magic value, digest state, byte length, and buffered partial block so hash operations can be paused and restored by the crypto API.

No filesystem state is persisted. Hardware-visible persistent state is limited to SRAM constants and descriptor-programmed engine state. Runtime suspend loses device SRAM, so `cc_pm_resume()` calls `cc_init_hash_sram()` to re-stage the constants.

## Dependencies And Integration Points

The file depends on the crypto API, `cc_request_mgr` for descriptor submission, `cc_buffer_mgr` for scatterlist and MLLI mapping, `cc_sram_mgr` for constant storage, CryptoCell descriptor setters from `cc_hw_queue_defs.h`, and hardware mode enums from the ccree driver. AEAD code also uses `cc_larval_digest_addr()` and digest length helpers for authenticated encryption hash phases.

Integration with the Linux crypto API is through `crypto_register_ahash()` and asynchronous completion callbacks. Integration with runtime PM is indirect through `cc_send_request()` and `cc_send_sync_request()`, which hold device power while descriptors are outstanding.

## Risks And Edge Cases

Descriptor sequence length is bounded by `CC_MAX_HASH_SEQ_LEN`; adding operations to setkey/final paths must preserve this limit. DMA mappings are bidirectional and cacheline-aligned; missing syncs around precomputed HMAC buffers would create stale key state. SHA-384/SHA-512 larval values require hi/lo word ordering and a larger digest length constant. `cc_larval_digest_addr()` depends on the exact SRAM copy order and on whether SM3 support is present; mismatches corrupt every later hash. Zero-length hash, HMAC with zero-length key, and MAC finalization after a full block have explicit special paths that are easy to regress.

## Test Signals

Useful signals are crypto self-tests for all registered hashes and HMAC/MACs, `tcrypt`/AF_ALG one-shot and update/final coverage, export/import tests across partial blocks, suspend/resume tests that run hashing after resume, DMA API debugging, and stress with fragmented scatterlists that force both DLLI and MLLI descriptor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.h

## Purpose

`cc_hash.h` defines the shared hash request state and exported hash/SRAM helper interfaces used by the CryptoCell hash implementation and other ccree modules. It is the contract between `cc_hash.c`, buffer mapping code, and AEAD code that needs hash larval and digest-length SRAM addresses.

## Important APIs, Types, And Functions

Constants define HMAC pad words, hardware digest-length sizes for older and newer revisions, maximum digest/block sizes, XCBC derived-key offsets, and `CC_EXPORT_MAGIC` for import/export validation. `struct aeshash_state` mirrors the state shape used for AES-XCBC/CMAC state size accounting. `struct ahash_req_ctx` stores all per-request buffers, DMA addresses, scatterlist state, MLLI metadata, double-buffer counts, and the XCBC update count.

Inline helpers `cc_hash_buf_cnt()`, `cc_hash_buf()`, `cc_next_buf_cnt()`, and `cc_next_buf()` select the current or alternate partial-block buffer based on `buff_index`. Exported functions are `cc_hash_alloc()`, `cc_init_hash_sram()`, `cc_hash_free()`, `cc_digest_len_addr()`, and `cc_larval_digest_addr()`.

## Control Flow

The header has no executable control flow beyond inline buffer selectors. Its definitions are consumed when crypto transforms set request DMA size, when buffer manager code fills partial blocks and MLLI tables, and when hash descriptors load or write state.

## State And Persistence Behavior

`struct ahash_req_ctx` is per asynchronous hash request, not persistent beyond the request unless exported through the crypto API. Its aligned buffers are DMA-facing and include digest result, current digest state, HMAC outer digest, digest byte count, and partial input blocks. The SRAM address helpers refer to device SRAM state initialized elsewhere.

## Dependencies And Integration Points

The header includes `cc_buffer_mgr.h`, so it shares `async_gen_req_ctx`, `mlli_params`, and DMA buffer type definitions. It depends on Linux crypto constants for AES and SHA sizes. It is included by `cc_hash.c`, AEAD setup code, and request/buffer paths that operate on hash request state.

## Risks And Edge Cases

Changing maximum digest or block sizes affects DMA mapping sizes, crypto statesize, and export/import layout. `CC_EXPORT_MAGIC` protects only against obvious format mismatch, not against mode mismatch. The double-buffer helpers assume `buff_index` is always 0 or 1. `xcbc_count` is used to distinguish empty, partial, and full-block MAC finalization cases.

## Test Signals

Compile coverage should catch structure/member contract breaks across `cc_hash.c` and `cc_buffer_mgr.c`. Runtime signals include successful hash export/import, fragmented update/final tests that switch buffers, and AES-XCBC/CMAC tests with empty input, one full block, and partial final blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_host_regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_host_regs.h

## Purpose

`cc_host_regs.h` is a generated register-offset and bitfield map for CryptoCell host-facing registers. It supplies symbolic offsets and field widths for interrupt handling, security/fuse status, boot capability discovery, version/signature reads, power-down control, host SRAM access, and component identification.

## Important APIs, Types, And Functions

The file defines macros only. Important groups include `CC_HOST_IRR_*` interrupt raw-status bits, `CC_HOST_IMR_*` interrupt mask bits, `CC_HOST_ICR_*` interrupt clear bits, `CC_HOST_SEP_SRAM_THRESHOLD_*`, `CC_HOST_SIGNATURE_*`, `CC_HOST_BOOT_*` hardware capability bits, `CC_HOST_VERSION_*`, key-valid registers, `CC_HOST_POWER_DOWN_EN_*`, input-pin removal bits, peripheral/component ID registers, and host SRAM data/address/ready registers.

## Control Flow

There is no control flow in this header. Runtime code combines these macros through `CC_REG(...)`, `cc_ioread()`, `cc_iowrite()`, and bit helpers. The request manager uses host interrupt bits for completion and CPP abort classification. Power management writes `HOST_POWER_DOWN_EN`. SRAM manager uses `HOST_SEP_SRAM_THRESHOLD` on older revisions.

## State And Persistence Behavior

The represented state is hardware MMIO state. Interrupt status and clear bits are transient. Boot/version/security bits describe hardware configuration. Power-down state persists in the device until runtime PM resume disables it. SRAM data registers expose volatile device SRAM access.

## Dependencies And Integration Points

This header is consumed by `cc_driver.c`, `cc_request_mgr.c`, `cc_pm.c`, `cc_sram_mgr.c`, debugfs, and FIPS/security handling. It must match the CryptoCell hardware revision layout, including the different signature/version offsets used by 630 and 712-class devices.

## Risks And Edge Cases

Wrong bit shifts can cause missed interrupts, failure to clear completion conditions, incorrect feature discovery, or unsafe power transitions. Host interrupt masks include both AES and SM abort bits by slot; request completion error reporting depends on these values matching hardware. The SRAM threshold must be word-aligned before the SRAM allocator trusts it.

## Test Signals

Boot logs should show correct hardware revision detection, no stuck interrupts, and successful request completions. Runtime PM suspend/resume should toggle power-down without losing later operation. Debugfs or register dumps can validate expected signature/version and interrupt-mask behavior on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_host_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hw_queue_defs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hw_queue_defs.h

## Purpose

`cc_hw_queue_defs.h` defines the six-word CryptoCell hardware descriptor format, enumerations for DMA/flow/setup/cipher fields, and inline setters that pack descriptor words. It is the main abstraction used by cipher, AEAD, hash, SRAM, and request manager code to build hardware command sequences.

## Important APIs, Types, And Functions

`struct cc_hw_desc` stores six 32-bit descriptor words. Macros derive bit masks from `cc_kernel_regs.h` field definitions. Enumerations describe AXI security, descriptor direction, DMA modes (`NO_DMA`, `DMA_SRAM`, `DMA_DLLI`, `DMA_MLLI`), flow modes, setup operations, hash padding/configuration, AES MAC selectors, hardware key slots, AES key sizes, and hash padding commands.

Setter functions include `hw_desc_init()`, `set_queue_last_ind_bit()`, `set_din_type()`, `set_din_no_dma()`, `set_cpp_crypto_key()`, `set_din_sram()`, `set_din_const()`, `set_din_not_last_indication()`, `set_dout_type()`, `set_dout_dlli()`, `set_dout_mlli()`, `set_dout_no_dma()`, `set_xor_val()`, `set_xor_active()`, `set_aes_not_hash_mode()`, `set_aes_xor_crypto_key()`, `set_dout_sram()`, `set_xex_data_unit_size()`, `set_multi2_num_rounds()`, `set_flow_mode()`, `set_cipher_mode()`, `set_hash_cipher_mode()`, `set_cipher_config0()`, `set_cipher_config1()`, `set_hw_crypto_key()`, `set_bytes_swap()`, `set_cmac_size0_mode()`, `set_key_size()`, `set_key_size_aes()`, `set_key_size_des()`, `set_setup_mode()`, and `set_cipher_do()`.

## Control Flow

The header has no runtime loop, but it controls descriptor construction order in callers. Callers initialize a descriptor, set DIN/DOUT fields, select flow and cipher mode, add setup operation and key/padding flags, then submit the sequence through the request manager. For 64-bit DMA builds, high address halves are packed into word 5.

## State And Persistence Behavior

Descriptors are transient command records. Once written to `DSCRPTR_QUEUE_WORD0`, hardware consumes the six words and updates engine state, SRAM, or DMA buffers depending on flow mode. The setters mutate only in-memory descriptor arrays.

## Dependencies And Integration Points

The header includes `cc_kernel_regs.h` for bitfield offsets and Linux `bitfield.h` for `FIELD_PREP`. It is used across the ccree driver wherever hardware work is described. `set_hash_cipher_mode()` contains an SM3-specific integration detail: it sets `AES_XOR_CRYPTO_KEY` to select the SM3 engine path for that hash mode.

## Risks And Edge Cases

These setters mostly OR fields into words; callers must start from `hw_desc_init()` or stale fields can survive. Field sizes limit DIN/DOUT sizes to descriptor bit widths, while MLLI entries have a smaller 16-bit per-entry limit. `set_key_size_aes()` expects byte sizes and converts to hardware codes; passing a code instead of bytes would program the wrong key length. Queue-last and DOUT-last are distinct bits and confusing them can hang flows or suppress completions.

## Test Signals

Descriptor dumps under `cc_dump_desc`, crypto self-tests for each flow mode, 64-bit DMA address testing, hardware-key/CPP paths, SM3 tests, and MLLI scatterlist tests provide useful validation that bit packing matches hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hw_queue_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_kernel_regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_kernel_regs.h

## Purpose

`cc_kernel_regs.h` is a generated register and bitfield map for CryptoCell descriptor queue and AXI monitor registers. It underpins descriptor packing and request completion accounting.

## Important APIs, Types, And Functions

The descriptor block defines completion counter, software reset, queue SRAM size, single-address enable, measure counter, queue word registers 0 through 5, queue watermark, and queue content fields. It also defines every descriptor word field: DIN mode/size/security/constant/not-last, DOUT mode/size/security/last/queue-last, flow/cipher/setup/key/padding fields, and high address bits. The AXI block defines inflight, completion, error, configuration, ACE constant, and cache parameter registers.

## Control Flow

There is no code flow. `cc_hw_queue_defs.h` consumes descriptor field definitions to pack commands, while `cc_request_mgr.c` reads `DSCRPTR_QUEUE_SRAM_SIZE`, writes queue words, reads `DSCRPTR_QUEUE_CONTENT`, and reads AXI completion counters through the driver-selected AXIM monitor offset.

## State And Persistence Behavior

Queue content and completion counters are live hardware state. Descriptor queue words are write-only command ingress from the driver's perspective. AXI monitor counters and error fields reflect transient bus activity and are cleared or consumed by hardware behavior.

## Dependencies And Integration Points

The header is included by `cc_hw_queue_defs.h` and indirectly by most CryptoCell operation builders. Queue size and content fields integrate with software queue admission in `cc_request_mgr.c`; AXI completion fields integrate with IRQ bottom-half completion processing.

## Risks And Edge Cases

Any mismatch between these field definitions and silicon causes global descriptor corruption. The completion counter is central to request dequeue; an incorrect field would desynchronize hardware completions from the software ring. The word-5 high-address fields matter only on 64-bit DMA builds, so they need coverage on systems with addresses above 4 GiB.

## Test Signals

Request manager initialization should read a queue size at or above `MIN_HW_QUEUE_SIZE`. Descriptor submission should reduce queue-content accounting without mismatch warnings. High-throughput crypto stress should not report empty software queue completions, AXI errors, or stalled queue availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_kernel_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_lli_defs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_lli_defs.h

## Purpose

`cc_lli_defs.h` defines CryptoCell linked-list item layout and limits for MLLI scatter/gather tables. It supports buffer manager code that converts Linux scatterlists into hardware-readable DMA list entries.

## Important APIs, Types, And Functions

Constants define descriptor DLLI size width, maximum MLLI entry size (`0xffff`), maximum data and associated-data entries, table alignment, maximum buffer groups, total entry budget, and the two-word LLI layout. Word 0 stores low address bits. Word 1 stores 16 bits of size and, on 64-bit DMA builds, 16 high address bits. Inline setters `cc_lli_set_addr()` and `cc_lli_set_size()` pack those fields using masks and `FIELD_PREP`.

## Control Flow

The header has no independent control flow. Buffer mapping code allocates MLLI tables, iterates scatterlist segments, writes each entry with these helpers, and then references the MLLI table from hardware descriptors.

## State And Persistence Behavior

LLI entries are transient DMA-visible memory. They persist only for the lifetime of the mapped crypto request and are unmapped or reused by buffer manager cleanup.

## Dependencies And Integration Points

The file depends on Linux types, DMA address width configuration, `GENMASK`, and `FIELD_PREP`. It integrates with `cc_buffer_mgr` and descriptor flows that use `DMA_MLLI` in `cc_hw_queue_defs.h`.

## Risks And Edge Cases

Each MLLI entry size is 16-bit, so larger scatterlist chunks must be split before encoding. Tables must be 32-bit aligned. On 64-bit DMA, only 16 high address bits are encoded, matching a 48-bit address assumption. Exceeding entry-count limits can corrupt adjacent MLLI workspace or force request mapping failure.

## Test Signals

Scatterlist-heavy hash, cipher, and AEAD tests should force MLLI paths. DMA API debugging and IOMMU tests with high physical addresses validate address packing. Large fragmented inputs should either succeed with split entries or fail cleanly before descriptor submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_lli_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.c

## Purpose

`cc_pm.c` implements runtime power management for the ccree CryptoCell device. It powers the hardware down when idle, restores clocks and registers on resume, and exposes small wrappers used by request submission to hold runtime PM references while hardware descriptors are outstanding.

## Important APIs, Types, And Functions

`cc_pm_suspend()` finalizes CryptoCell registers, enables `HOST_POWER_DOWN_EN`, and disables the device clock. `cc_pm_resume()` enables the clock, waits for reset completion, disables power-down, reinitializes common registers, handles TEE/FIPS errors, and reinitializes hash SRAM constants. `ccree_pm` exports runtime PM ops. `cc_pm_get()` wraps `pm_runtime_get_sync()` and unwinds failed gets; `cc_pm_put_suspend()` calls `pm_runtime_put_autosuspend()`.

## Control Flow

Asynchronous and synchronous request submission call `cc_pm_get()` before queue admission. Completion processing calls `cc_pm_put_suspend()` after each dequeued request callback. Runtime suspend runs only when the PM core decides the device is idle. Resume must complete register and SRAM initialization before any queued descriptor sequence can rely on hardware state.

## State And Persistence Behavior

Runtime suspend intentionally drops volatile hardware state: clocks are disabled and the power-down bit is set. Resume restores register programming and hash SRAM constants, but per-request and per-transform DMA memory remains host-side. FIPS/TEE status may be detected after power-down and handled during resume.

## Dependencies And Integration Points

The file depends on Linux runtime PM, clocks, interrupt headers, ccree driver init/fini helpers, SRAM manager, hash SRAM initialization, and FIPS handling. It is included through `cc_pm.h` by the request manager, making PM lifetime management part of request submission semantics.

## Risks And Edge Cases

If resume cannot enable the clock or reset does not complete, future crypto requests fail. Forgetting to reinitialize hash SRAM after resume would break hash and AEAD operations using SRAM larval constants. PM reference imbalance in the request manager would either prevent autosuspend or suspend the device with descriptors still active.

## Test Signals

Enable runtime PM autosuspend and run crypto self-tests before and after idle suspend. Logs should not show reset timeout or `init_cc_regs` errors. Hash operations after resume validate SRAM reload. PM debug counters should show balanced gets/puts under concurrent crypto load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.h

## Purpose

`cc_pm.h` declares the ccree runtime PM interface and provides no-op fallbacks when `CONFIG_PM` is disabled. It lets request submission code use a uniform API independent of kernel PM configuration.

## Important APIs, Types, And Functions

The header defines `CC_SUSPEND_TIMEOUT`, declares `extern const struct dev_pm_ops ccree_pm`, `cc_pm_get()`, and `cc_pm_put_suspend()` under `CONFIG_PM`, and provides inline stubs that return success/do nothing otherwise.

## Control Flow

There is no runtime control flow except the compile-time branch. With PM enabled, callers enter `cc_pm.c`. Without PM, request submission proceeds without runtime PM references.

## State And Persistence Behavior

The header owns no state. Its stubs imply the hardware remains available by other means when runtime PM support is absent.

## Dependencies And Integration Points

It includes `cc_driver.h` and is consumed by `cc_request_mgr.c` and the platform driver PM registration path. The PM ops are attached to the device driver outside this header.

## Risks And Edge Cases

The no-op fallback means PM-only bugs may be hidden on kernels built without `CONFIG_PM`. Callers must pair `cc_pm_get()` and `cc_pm_put_suspend()` even though that balance is compile-time invisible when PM is disabled.

## Test Signals

Build both with and without `CONFIG_PM`. With PM enabled, runtime suspend/resume crypto stress should pass. Without PM, request manager code should compile and run with the inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.c

## Purpose

`cc_request_mgr.c` is the central descriptor submission and completion engine for the ccree driver. It maintains a software FIFO matching hardware completions, writes six-word descriptors into the hardware queue, handles synchronous initialization requests, manages a backlog for async requests when the hardware queue is full, and releases runtime PM references when requests complete.

## Important APIs, Types, And Functions

`struct cc_req_mgr_handle` stores hardware queue capacity, free-slot accounting, software request ring, completion counters, locks, dummy completion descriptor, optional workqueue/tasklet, and backlog list. `struct cc_bl_item` stores a deferred request and copied descriptor sequence. Public APIs are `cc_req_mgr_init()`, `cc_req_mgr_fini()`, `cc_send_request()`, `cc_send_sync_request()`, `send_request_init()`, and `complete_request()`.

Important internals include `enqueue_seq()`, `cc_queues_status()`, `cc_do_send_request()`, `cc_enqueue_backlog()`, `cc_proc_backlog()`, `proc_completions()`, `cc_axi_comp_count()`, and `comp_handler()`. `cc_cpp_int_mask()` maps CPP algorithm/slot completion status to abort interrupt masks using `array_index_nospec()`.

## Control Flow

Initialization allocates the manager, initializes locks and backlog, sets up a tasklet or workqueue, reads hardware queue size, validates it, allocates a coherent dummy completion word, and builds a completion descriptor. Async submission calls `cc_pm_get()`, takes the hardware lock, checks software and hardware capacity, optionally copies the request into the backlog and returns `-EBUSY`, or writes descriptors and returns `-EINPROGRESS`. Backlogged requests are retried from the completion tasklet after space becomes available.

Synchronous submission sets a completion callback, holds runtime PM, waits until enough room exists for the request plus dummy completion descriptor, enqueues both, and blocks until the dummy completion completes. `send_request_init()` is the early/init path: it polls for room, marks the last supplied descriptor as queue-last, writes the sequence, and refreshes free-slot accounting.

Interrupt handling starts in `complete_request()`, which completes hardware-queue waiters and schedules the bottom half. `comp_handler()` clears/masks completion interrupts, samples AXI completion counts, calls `proc_completions()` until drained, unmasks completion interrupts, then processes backlog. `proc_completions()` dequeues software requests, derives CPP error status if relevant, invokes user callbacks, advances the ring tail, and drops runtime PM references.

## State And Persistence Behavior

The manager owns volatile in-kernel state only: software FIFO head/tail, backlog list, free-slot estimates, and AXI completion counts. Hardware queue contents and AXI monitor counters are MMIO state. There is no persistence across driver remove or reboot; `cc_req_mgr_fini()` tears down tasklet/workqueue and coherent memory.

## Dependencies And Integration Points

The file depends on `cc_driver` register helpers and global IRQ state, `cc_hw_queue_defs.h` descriptors, `cc_pm` runtime PM wrappers, the crypto async request backlog contract, and callbacks supplied by hash/cipher/AEAD modules through `struct cc_crypto_req`. The platform IRQ handler in `cc_driver.c` calls `complete_request()`.

## Risks And Edge Cases

Software FIFO size must remain a power of two because head/tail wrap uses `MAX_REQUEST_QUEUE_SIZE - 1`. A completion count without a queued request indicates serious desynchronization and is logged. Backlog descriptors are copied into a fixed `CC_MAX_DESC_SEQ_LEN` array; callers must not submit longer sequences. PM references must be released exactly once per accepted request, including CPP error completions. `cc_send_sync_request()` waits interruptibly for queue space but does not propagate interruption from that wait.

## Test Signals

High-concurrency crypto stress should exercise queue-full and backlog paths without dropped requests. `CRYPTO_TFM_REQ_MAY_BACKLOG` callers should receive `-EBUSY` then `-EINPROGRESS` notification. Runtime PM counters should remain balanced. Forced CPP aborts should surface as request errors. Descriptor queue mismatch and empty-queue completion logs indicate bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.h

## Purpose

`cc_request_mgr.h` declares the public request-manager interface used by ccree crypto modules and initialization code. It hides the software queue, backlog, completion tasklet, and hardware queue details behind descriptor submission functions.

## Important APIs, Types, And Functions

The header includes `cc_hw_queue_defs.h` to expose `struct cc_hw_desc`. It declares `cc_req_mgr_init()`, `cc_req_mgr_fini()`, `cc_send_request()` for asynchronous crypto requests, `cc_send_sync_request()` for blocking internal flows, `send_request_init()` for initialization-time descriptor sequences, and `complete_request()` for IRQ dispatch.

## Control Flow

Callers build descriptor arrays, fill a `struct cc_crypto_req` callback/argument, and submit through `cc_send_request()` or `cc_send_sync_request()`. The platform interrupt path calls `complete_request()` to defer completion processing.

## State And Persistence Behavior

The header declares stateful operations but owns no state. State is private to `cc_request_mgr.c` and stored in `drvdata->request_mgr_handle`.

## Dependencies And Integration Points

The API is used by hash, cipher, AEAD, SRAM initialization, FIPS, and driver init paths. It depends on `struct cc_drvdata`, `struct cc_crypto_req`, and `struct crypto_async_request` being visible from included driver/crypto headers in translation units.

## Risks And Edge Cases

The API does not encode descriptor length limits in the type system. Callers must obey the manager's maximum copied backlog sequence length and set queue-last descriptors correctly for flows that need hardware engine release. Asynchronous callbacks must tolerate `-EINPROGRESS` backlog notifications and final completions.

## Test Signals

Build coverage across all ccree modules catches declaration drift. Runtime validation is indirect through successful async hash/cipher/AEAD operations, synchronous setkey/init descriptor flows, and IRQ completion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.c

## Purpose

`cc_sram_mgr.c` provides a simple monotonic allocator for CryptoCell internal SRAM and helper code to build descriptor sequences that copy constant words into SRAM. It is used for MLLI workspace allocation and hash/AEAD constant staging.

## Important APIs, Types, And Functions

`cc_sram_mgr_init()` initializes `drvdata->sram_free_offset`, using `HOST_SEP_SRAM_THRESHOLD` on hardware older than revision 712 to skip ROM-reserved SRAM. `cc_sram_alloc()` returns a 4-byte-aligned SRAM offset or `NULL_SRAM_ADDR`. `cc_set_sram_desc()` appends BYPASS descriptors that write each source word as a constant to consecutive SRAM addresses.

## Control Flow

Initialization sets the starting offset once. Each allocation validates 4-byte alignment and remaining capacity, returns the current offset, and advances the free pointer. Constant-copy setup iterates over source words, initializing one descriptor per word with `set_din_const()`, `set_dout_sram()`, and `set_flow_mode(BYPASS)`.

## State And Persistence Behavior

The allocator state is only `drvdata->sram_free_offset`; it is monotonic and has no free operation. SRAM contents are volatile and lost across power-down, so users such as hash code must re-copy constants during resume. Allocation layout persists only for the driver lifetime.

## Dependencies And Integration Points

The file depends on `cc_driver.h`, host register definitions, descriptor setters, and `cc_sram_mgr.h`. It is called during driver probe before hash/cipher/AEAD resources are allocated, and by hash initialization to create SRAM-copy descriptors submitted through the request manager.

## Risks And Edge Cases

All allocations must be multiples of 4. The older-hardware threshold must itself be 4-byte aligned or initialization fails. There is no deallocation or compaction, so allocation order and size calculations must be stable. `cc_set_sram_desc()` assumes the caller provided enough descriptor slots for one descriptor per word.

## Test Signals

Probe logs should not show invalid SRAM threshold or insufficient space. Hash registration validates enough SRAM for digest constants. AEAD and MLLI-heavy operations validate shared SRAM allocation pressure. Suspend/resume tests validate that contents, not allocation offsets, are restored by users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.h

## Purpose

`cc_sram_mgr.h` declares the internal SRAM allocator and SRAM descriptor-copy helper for the ccree driver. It provides a compact contract for modules that need fixed CryptoCell SRAM workspace.

## Important APIs, Types, And Functions

The header defines default `CC_CC_SRAM_SIZE` as 4096 if not supplied by the build, forward-declares `struct cc_drvdata`, defines `NULL_SRAM_ADDR`, and declares `cc_sram_mgr_init()`, `cc_sram_alloc()`, and `cc_set_sram_desc()`.

## Control Flow

There is no executable control flow in the header. The declarations support probe-time initialization, monotonic allocation, and descriptor construction in implementation files.

## State And Persistence Behavior

The header owns no state but documents that SRAM allocation returns offsets into volatile device SRAM. `NULL_SRAM_ADDR` is `(u32)-1`, so valid users must compare against that sentinel rather than zero.

## Dependencies And Integration Points

It is included by hash, AEAD, PM, driver, and SRAM manager code. `cc_set_sram_desc()` depends on `struct cc_hw_desc` being visible in callers through included descriptor definitions.

## Risks And Edge Cases

The default 4 KiB size must match the targeted hardware or platform override. Treating address 0 as allocation failure would be wrong because SRAM pools can start at offset 0 on newer hardware. Users must remember there is no free operation.

## Test Signals

Build coverage catches signature drift. Probe and crypto registration validate allocation sizes. Tests on older and newer CryptoCell revisions validate both threshold-based and zero-based SRAM pool starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Kconfig

## Purpose

`drivers/crypto/chelsio/Kconfig` exposes the Chelsio T6 crypto co-processor driver as `CONFIG_CRYPTO_DEV_CHELSIO`. It controls whether the `chcr` module is built and declares the crypto-library dependencies needed by that driver.

## Important APIs, Types, And Functions

The single symbol is `CRYPTO_DEV_CHELSIO`, a tristate named "Chelsio Crypto Co-processor Driver". It depends on `CHELSIO_T4` and selects `CRYPTO_LIB_AES`, `CRYPTO_LIB_GF128MUL`, SHA-1/SHA-256/SHA-512 libraries, and `CRYPTO_AUTHENC`. The help text identifies the module name as `chcr`.

## Control Flow

Kconfig evaluation determines whether the symbol is unavailable, built-in, or module. If enabled, the Makefile in the same directory builds the Chelsio crypto objects according to this symbol.

## State And Persistence Behavior

There is no runtime state. The selected symbol persists in kernel configuration and changes build output and module availability.

## Dependencies And Integration Points

The dependency on `CHELSIO_T4` ties this crypto driver to the Chelsio cxgb4 network adapter infrastructure. Selected crypto libraries provide AES, GF(2^128), SHA, and authenc support used by the implementation objects.

## Risks And Edge Cases

Using `select` forces library symbols on when the driver is enabled, so dependency correctness matters. If `CHELSIO_T4` is disabled, the crypto option is hidden even if crypto subsystem support is present. The help URLs are informational and not part of build behavior.

## Test Signals

Configuration tests should verify `CONFIG_CRYPTO_DEV_CHELSIO=m` builds `chcr.ko` when `CHELSIO_T4=m/y`. `scripts/config` or `make menuconfig` should show the symbol only with the dependency satisfied. Module load tests require compatible Chelsio hardware or graceful no-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Makefile

## Purpose

`drivers/crypto/chelsio/Makefile` wires the Chelsio crypto driver into Kbuild. It adds the cxgb4 network-driver include path and builds the `chcr` object when `CONFIG_CRYPTO_DEV_CHELSIO` is enabled.

## Important APIs, Types, And Functions

`ccflags-y` adds `-I $(srctree)/drivers/net/ethernet/chelsio/cxgb4`, allowing Chelsio crypto code to include cxgb4 headers. `obj-$(CONFIG_CRYPTO_DEV_CHELSIO) += chcr.o` registers the module/built-in object. `chcr-objs := chcr_core.o chcr_algo.o` composes the final object from core and algorithm implementation files.

## Control Flow

Kbuild expands `obj-y` or `obj-m` depending on the Kconfig symbol. It compiles `chcr_core.o` and `chcr_algo.o`, links them into `chcr.o`, and either links that into the kernel or emits `chcr.ko`.

## State And Persistence Behavior

There is no runtime state. Build outputs depend on configuration and source timestamps.

## Dependencies And Integration Points

The include path is the integration bridge to the Chelsio T4/T6 network driver. The object list matches the driver module named in Kconfig help.

## Risks And Edge Cases

The Makefile assumes cxgb4 headers are available at the srctree path. Adding implementation files requires updating `chcr-objs`; otherwise code may compile in isolation but not be linked. Include-path coupling can break if the network driver directory is reorganized.

## Test Signals

`make M=drivers/crypto/chelsio` or a full kernel build with `CONFIG_CRYPTO_DEV_CHELSIO=m/y` should produce `chcr.o`/`chcr.ko` from both object files. Header dependency errors usually indicate cxgb4 include path drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Makefile -->
