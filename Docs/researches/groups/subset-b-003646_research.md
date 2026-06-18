# Research: subset-b-003646

Grouped research for Adreno GMU HFI, preemption, A8xx GPU bring-up/recovery, device registration, and Gen7 snapshot table headers. Each source file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.c

## Purpose

`a6xx_hfi.c` implements the host-to-GMU HFI command protocol used by A6xx, A7xx-adjacent, and A8xx Adreno GMU firmware paths. It owns shared HFI queue initialization, circular queue reads/writes, blocking command/ack sequencing, target-specific performance and bandwidth table construction, firmware feature enablement, frequency/bandwidth votes, and slumber preparation.

## Important APIs, Types, And Functions

The public entry points are `a6xx_hfi_init()`, `a6xx_hfi_start()`, `a6xx_hfi_stop()`, `a6xx_hfi_set_freq()`, and `a6xx_hfi_send_prep_slumber()`, declared via `a6xx_gmu.h`. Core transport helpers are `a6xx_hfi_queue_read()`, `a6xx_hfi_queue_write()`, `a6xx_hfi_wait_for_msg_interrupt()`, `a6xx_hfi_wait_for_ack()`, and `a6xx_hfi_send_msg()`. Message helpers include GMU init/version, perf table, BW table, ACD, IFPC, core firmware start, start, test, frequency vote, and prepare-slumber commands.

The file relies heavily on packed message structs from `a6xx_hfi.h`, GMU state in `struct a6xx_gmu`, target classification helpers such as `adreno_is_a8xx()`, `adreno_is_a619()`, `adreno_is_a740_family()`, and register accessors `gmu_read/write`, `gmu_poll_timeout`, and `gmu_write()`.

## Control Flow

Queue initialization in `a6xx_hfi_init()` lays out the queue table at the front of `gmu->hfi`, followed by queue headers and three 4 KiB data rings: command, response, and debug. `a6xx_hfi_queue_init()` sets shared header metadata, initializes the spinlock and sequence number, records queue IOVA, and clears history.

Command flow starts in `a6xx_hfi_send_msg()`: a sequence number is atomically allocated, the first dword is overwritten with an HFI header, the command is written into the command ring, and the function waits for a response with the same sequence number. `a6xx_hfi_queue_write()` validates circular-buffer free space, stores packet dwords, pads non-legacy queues to 4-dword alignment, performs `dma_mb()`, publishes `write_index`, and raises `REG_A6XX_GMU_HOST2GMU_INTR_SET`. Response flow waits for `GMU2HOST_INTR_INFO_MSGQ`, clears the interrupt, drains the response queue, skips firmware error records and unrelated sequence numbers, and returns optional payload data.

Startup splits on `gmu->legacy`. Legacy `a6xx_hfi_start_v1()` sends GMU init, FW version exchange, v1 perf table, BW table, then a test/end marker. Modern `a6xx_hfi_start()` sends perf and BW tables, enables ACD and IFPC when configured, starts core firmware, and then sends the generic start message.

Performance table generation is target dependent. Classic A6xx fills fixed HFI message structs from `gmu->gx_arc_votes`, `cx_arc_votes`, `gpu_freqs`, and `gmu_freqs`. A8xx uses `HFI_H2F_MSG_TABLE` with variable-length `struct a6xx_hfi_table`, including GX ARC, dependency ARC, and GPU frequency columns plus CX votes. Bandwidth table generation either consumes catalog BCM names through command DB/TCS helpers when available or selects one of the hard-coded target tables for A618, A619, A640, A650, A660, A663, A690, 7c3, A730, A740, and generic A6xx.

## State And Persistence Behavior

Persistent runtime state lives in `gmu->queues[]`, shared queue headers/data inside the mapped HFI BO, `gmu->bw_table`, `gmu->acd_table`, frequency/vote arrays, and queue history buffers. Queue read/write indexes are shared with firmware and protected by memory barriers. Command writes are serialized with `queue->lock`; response reads are not spinlocked and rely on host-side single-reader behavior plus firmware producer semantics. `gmu->bw_table` is lazily allocated with `devm_kzalloc()` and reused across sends until device teardown.

## Dependencies And Integration Points

This code integrates with GMU boot/resume in `a6xx_gmu.c`, which allocates HFI memory, programs queue table registers, enables HFI interrupts, and calls `a6xx_hfi_start()`. GPU frequency changes call `a6xx_hfi_set_freq()`. Runtime suspend/slumber calls `a6xx_hfi_send_prep_slumber()`. Crash dump code consumes `queue->history` to decode recent HFI traffic. The code depends on Qualcomm command DB names and TCS/BCM encoding when catalog BCM tables are present.

## Risks

The response read path uses `BUG_ON(HFI_HEADER_SIZE(hdr) > dwords)`, intentionally crashing on impossible firmware/memory corruption. `a8xx_hfi_send_perf_table()` does not check `kzalloc()` failure before dereferencing `tbl`, which is a real allocation-failure risk. Message name logging indexes `a6xx_hfi_msg_id[id]`; new IDs must be added to the name table or error paths can access unset entries. Bandwidth tables are hardware-specific magic values; wrong addresses or wait masks can prevent boot, DVFS, or low-power entry. The blocking wait path loops around GPU coredump completion, so fault recovery and HFI waits are coupled.

## Test Signals

Useful signals are successful GMU boot/resume, no HFI timeout logs, no response queue empty errors, correct GPU frequency/bandwidth transitions, IFPC/ACD enablement on configured devices, and clean `a6xx_hfi_stop()` without non-empty queue warnings. Hardware tests should cover legacy and modern GMUs, A8xx variable perf tables, command DB generated BW tables, and every hard-coded target BW fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.h

## Purpose

`a6xx_hfi.h` defines the packed shared-memory ABI used by the host driver and GMU firmware for HFI queues and messages. It is a protocol contract rather than executable logic: layout, field order, queue IDs, message IDs, feature IDs, table IDs, and payload structs must match firmware expectations.

## Important APIs, Types, And Functions

The queue ABI is defined by `struct a6xx_hfi_queue_table_header`, `struct a6xx_hfi_queue_header`, and host-only `struct a6xx_hfi_queue`. Queue constants include `HFI_MAX_QUEUES`, `HFI_COMMAND_QUEUE`, `HFI_RESPONSE_QUEUE`, and header extraction macros `HFI_HEADER_ID()`, `HFI_HEADER_SIZE()`, and `HFI_HEADER_SEQNUM()`.

Message structs cover response/error packets, GMU init, firmware version, v1 and modern perf tables, BW tables, test/start/core-fw-start, feature control, generic variable tables, GX BW/perf votes, prepare-slumber, ACD tables, CLX tables, and mitigation limits. Feature constants under `struct a6xx_hfi_msg_feature_ctrl` enumerate GMU firmware features such as DCVS, preemption, IFPC, ACD, CLX, LPAC, HW fence, DMS, AQE, and fast context destroy.

## Control Flow

There is no runtime control flow in this header. The control relationship is structural: callers allocate and fill one of the packed structs, `a6xx_hfi_send_msg()` writes a header into the first dword, and firmware interprets the remaining dwords according to the ID. Variable table flow uses `struct a6xx_hfi_table` followed by flexible `entry[]` records; fixed messages use packed arrays and scalar fields.

## State And Persistence Behavior

The packed structs describe persistent shared memory observed by firmware. Queue headers contain firmware-visible `read_index`, `write_index`, watermarks, dropped counts, and request flags. Host-only `struct a6xx_hfi_queue` persists pointers, a spinlock, a command sequence counter, and an eight-entry history ring for devcoredump decoding.

## Dependencies And Integration Points

`a6xx_hfi.c` is the primary consumer. `a6xx_gmu.h` embeds `struct a6xx_hfi_queue queues[HFI_MAX_QUEUES]`, `struct a6xx_hfi_acd_table`, and `struct a6xx_hfi_msg_bw_table *bw_table`. Crash dump code reads queue history. Firmware compatibility depends on the exact values of the HFI IDs, table IDs, and feature IDs.

## Risks

All protocol structs are `__packed`; changing field order, widening fields, or removing padding will silently break firmware ABI. Fixed array sizes such as 16 GPU perf levels, 4 GMU perf levels, 16 BW levels, 8 DDR commands, and 6 CNOC commands must match all table builders. `HFI_RESPONSE_PAYLOAD_SIZE` is hard-coded to 16 dwords; payload-copy users must not request more meaningful data than firmware returns. New message IDs need coordinated updates in sender code and debug name tables.

## Test Signals

Build coverage catches syntax and some type mismatches, while real validation comes from GMU boot handshakes, firmware ACKs for each message, devcoredump HFI history readability, and successful operation across legacy and modern HFI firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.c

## Purpose

`a6xx_preempt.c` implements ringbuffer preemption for A6xx-style Adreno GPUs with more than one DRM scheduler ring. It allocates per-ring preemption records and SMMU context buffers, initializes hardware state, triggers context switches, handles completion interrupts, updates ring write pointers, and recovers from stuck or failed preemption.

## Important APIs, Types, And Functions

Public functions are `a6xx_preempt_init()`, `a6xx_preempt_hw_init()`, `a6xx_preempt_trigger()`, `a6xx_preempt_irq()`, and `a6xx_preempt_fini()`. Local helpers include the watchdog `a6xx_preempt_timer()`, postamble builders `preempt_prepare_postamble()` and `preempt_disable_postamble()`, keepalive voting via `a6xx_preempt_keepalive_vote()`, and `preempt_init_ring()`.

The implementation depends on shared inline helpers from `a6xx_preempt.h`: `try_preempt_state()`, `set_preempt_state()`, `update_wptr()`, and `get_next_ring()`. It uses `struct a6xx_preempt_record` and `struct a7xx_cp_smmu_info` from `a6xx_gpu.h`.

## Control Flow

Initialization exits early for single-ring GPUs. For each ring, `preempt_init_ring()` allocates a write-combined private GEM BO for the preemption record and another GPU-readonly BO for SMMU info. It writes default ring base, RB control, magic values, TTBR/context defaults, and BV rptr address, then allocates a postamble BO and sets up a watchdog timer. Any allocation failure disables preemption by cleaning up and forcing `gpu->nr_rings = 1`.

Hardware init resets per-ring records, writes zero to `REG_A6XX_CP_CONTEXT_SWITCH_SMMU_INFO`, enables GMEM save/restore, resets the atomic preemption state to `PREEMPT_NONE`, initializes the evaluation lock, and starts on ring 0.

`a6xx_preempt_trigger()` serializes candidate evaluation with `eval_lock`, transitions `PREEMPT_NONE -> PREEMPT_START`, computes `CP_CONTEXT_SWITCH_CNTL`, and asks `get_next_ring()` for the highest-priority non-empty ring. If no switch is needed, it refreshes the current ring WPTR and returns to `PREEMPT_NONE`. Otherwise it updates the target ring's SMMU info and preemption record under `ring->preempt_lock`, clears `restore_wptr`, votes keepalive on, fenced-writes target SMMU and restore-record addresses, records `next_ring`, starts a 10-second watchdog, toggles the postamble depending on sysprof state, transitions to `PREEMPT_TRIGGERED`, and writes context-switch control.

`a6xx_preempt_irq()` transitions `PREEMPT_TRIGGERED -> PREEMPT_PENDING`, cancels the watchdog, verifies the STOP bit cleared, installs `next_ring` as `cur_ring`, updates deferred WPTR state, returns to `PREEMPT_NONE`, votes keepalive off, traces completion, and retriggers to catch skipped requests.

## State And Persistence Behavior

Persistent state is in `a6xx_gpu`: atomic `preempt_state`, `cur_ring`, `next_ring`, per-ring record BO pointers/IOVAs, per-ring SMMU-info BOs/IOVAs, postamble BO/IOVA/length, `postamble_enabled`, feature flags `preempt_level`, `uses_gmem`, `skip_save_restore`, `eval_lock`, and `preempt_timer`. Each ring stores `restore_wptr` and memptr TTBR/context fields used during switch setup.

## Dependencies And Integration Points

`a6xx_gpu.c` calls preemption during GPU init, IRQ handling, retire events, and submissions. Register writes use `a6xx_fenced_write()` so CP-visible writes are sequenced. GMU keepalive prevents power collapse while a context switch is in flight. Tracepoints expose trigger and completion events. Recovery uses `gpu->worker` and `recover_work`.

## Risks

The state machine is race-sensitive. Missed barriers or unprotected WPTR updates can lose submissions or double-write ring pointers. The watchdog forces recovery after 10 seconds, but if recovery cannot run the GPU may remain stuck with keepalive asserted. `a6xx_preempt_fini()` only frees `preempt_bo[]` and not the SMMU/postamble BOs in this file, so ownership must be checked in wider teardown. The A6xx and A8xx implementations are near-duplicates, making drift likely.

## Test Signals

Key signals are successful multi-ring scheduling under load, tracepoint pairs for trigger/irq, no preemption timeout logs, correct recovery when STOP remains set, no lost fences when switching away from or back to the current ring, and stable behavior when sysprof enables/disables postamble handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.h

## Purpose

`a6xx_preempt.h` provides inline helpers for the A6xx/A8xx preemption state machine, deferred write-pointer updates, and next-ring selection. The helpers are shared by both preemption implementations and are deliberately small enough to inline into hot interrupt/submit paths.

## Important APIs, Types, And Functions

`try_preempt_state()` performs an atomic compare/exchange on `a6xx_gpu->preempt_state`. `set_preempt_state()` force-sets the state with barriers before and after the atomic store. `update_wptr()` writes a deferred ring WPTR to `REG_A6XX_CP_RB_WPTR` when `ring->restore_wptr` is set. `get_next_ring()` scans rings in priority order and returns the first non-empty candidate.

## Control Flow

The trigger path calls `try_preempt_state(PREEMPT_NONE, PREEMPT_START)` to claim preemption evaluation. IRQ paths call `try_preempt_state(PREEMPT_TRIGGERED, PREEMPT_PENDING)` to accept completions only for in-flight switches. `update_wptr()` locks the ring, checks the deferred flag, fetches `get_wptr(ring)`, uses `a6xx_fenced_write()`, then clears the flag. `get_next_ring()` locks each ring long enough to compare WPTR and RPTR. For the current ring, it treats the ring as empty when `memptrs->fence` matches `a6xx_gpu->last_seqno[i]`.

## State And Persistence Behavior

The helpers manipulate only existing persistent state: atomic `preempt_state`, per-ring `preempt_lock`, ring `restore_wptr`, ring memptr fence/context fields, and current-ring metadata. Memory ordering is explicit because state is observed across submission, IRQ, timer, and recovery contexts.

## Dependencies And Integration Points

Both `a6xx_preempt.c` and `a8xx_preempt.c` include this header. It depends on `a6xx_gpu.h` for `enum a6xx_preempt_state`, `struct a6xx_gpu`, register definitions, `shadowptr()`, and `a6xx_fenced_write()`. `get_next_ring()` relies on `gpu->funcs->get_rptr()` and the DRM/MSM ringbuffer model.

## Risks

The helpers assume the caller has selected the correct generation-specific register set for context switch control; only WPTR uses the shared A6xx register. `set_preempt_state()` can force transitions, so callers must use it only when they have already excluded competing transitions. `get_next_ring()` priority is fixed by ring index and may starve lower-priority rings under sustained higher-priority load.

## Test Signals

Tests should exercise concurrent submissions while preemption is being triggered, ring priority selection, deferred WPTR restore, current-ring empty detection by fence sequence, and state transitions under normal IRQ and timeout recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_gpu.c

## Purpose

`a8xx_gpu.c` implements generation-8 Adreno GPU operations plugged into the shared MSM/Adreno GPU framework. It covers aperture-controlled pipe/slice register access, slice discovery, idle/flush behavior, hardware clock gating, CP register protection, UBWC and non-context register programming, CP/power-up initialization, full hardware bring-up, recovery, fault decoding, interrupt handling, LLCC activation, bus halt, timestamp, busy counters, and progress reporting.

## Important APIs, Types, And Functions

Externally used functions include `a8xx_gpu_get_slice_info()`, `a8xx_flush()`, `a8xx_hw_init()`, `a8xx_recover()`, `a8xx_fault_handler()`, `a8xx_irq()`, `a8xx_llc_activate()`, `a8xx_bus_clear_pending_transactions()`, `a8xx_gmu_get_timestamp()`, `a8xx_gpu_busy()`, and `a8xx_progress()`.

Important local helpers are the aperture helpers (`a8xx_aperture_slice_set/acquire/release/clear`, `a8xx_write_pipe()`, `a8xx_read_pipe_slice()`), `a8xx_idle()`, `a8xx_set_hwcg()`, `a8xx_set_cp_protect()`, `a8xx_set_ubwc_config()`, `a8xx_nonctxt_config()`, `a8xx_patch_pwrup_reglist()`, `a8xx_preempt_start()`, `a8xx_cp_init()`, `hw_init()`, fault-block decoders, CP fault IRQ handling, hang-detect IRQ handling, and SW fuse handling.

## Control Flow

Pipe-specific register access is serialized through `a6xx_gpu->aperture_lock` and `REG_A8XX_CP_APERTURE_CNTL_HOST`; the cached aperture value avoids redundant writes. Slice discovery starts from catalog `max_slices`, masks with `REG_A8XX_CX_MISC_SLICE_ENABLE_FINAL` for Gen2+, and updates chip ID/name to encode active slice count.

`a8xx_hw_init()` takes the GMU lock and calls `hw_init()`. The bring-up sequence asserts GMU OOB GPU ownership, clears cached aperture and bus halts, disables secure memory ranges, programs GMEM/trap/UBWC/perf counters, emits non-context register lists, enables fault detection, configures GMU busy counters, programs CP protection, enables GMEM save/restore, masks per-pipe/global interrupts, calls `adreno_hw_init()`, programs SQE/AQE firmware bases and ringbuffer registers, calls `a8xx_preempt_hw_init()`, starts SQE, sends CP init packets, exits secure mode via zap shader or SECVID fallback, writes GMEM protection after non-secure transition, patches the power-up register list once, enables hardware clock gating, yields the ringbuffer for preemption, clears GMU OOB, and restores perf-counter OOB if sysprof is active.

Flush behavior is preemption-aware: it copies `ring->next` to `ring->cur`, computes WPTR, fenced-writes WPTR only if the ring is current and no preemption is active, otherwise marks `restore_wptr` for the preemption completion path.

Interrupt flow reads/clears `REG_A8XX_RBBM_INT_0_STATUS`, optionally filters error IRQs, dispatches hang detect, AHB, CP HW errors, ATB, UCHE, SW fuse, retire/cache flush, and CP SW preemption completion. Fatal paths disable interrupts and queue recovery.

Recovery marks the GPU hung, halts SQE, temporarily hides active submits from runtime suspend warnings, forces CX power-domain collapse through genpd notification, rebalances runtime PM refs, reinitializes hardware, and clears `hung`.

## State And Persistence Behavior

Persistent state includes `cached_aperture`, `slice_mask`, `pwrup_reglist_ptr` contents and `pwrup_reglist_emitted`, `cur_ring`, per-ring shadow values, runtime PM active submit counts during recovery, GMU status bits, and LLCC slice activation state. Register programming persists in hardware until reset or power collapse. The pwrup reglist stores IFPC/preemption register restore pairs plus dynamic aperture/address/data triplets for CP restoration.

## Dependencies And Integration Points

`a6xx_gpu.c` installs these callbacks in `a8xx_gpu_funcs`. The file integrates with GMU OOB and power counters, LLCC, qcom UBWC config, firmware loading/zap shader, DRM scheduler rings, MSM fault handling, A8xx preemption, runtime PM/genpd, and catalog register lists/protection tables.

## Risks

Aperture selection is global hardware state; missing release/clear or stale cache can direct reads/writes to the wrong pipe/slice. Bring-up order is fragile around secure-mode exit, GMEM protection, CP init, SQE start, and GMU OOB ownership. Recovery manipulates runtime PM refs and `active_submits`; imbalance can deadlock suspend/resume. `a8xx_progress()` always returns true, reducing hangcheck usefulness. Many register constants are hardware magic values with limited software validation.

## Test Signals

Signals include successful boot across A8xx variants, correct active-slice chip name updates, clean idle after CP init and secure-mode exit, no aperture-related misprogramming across BR/BV/DDE pipes, interrupt recovery for CP faults and hang detect, LLCC activation, accurate GMU timestamp/busy counters, and stress under multi-ring preemption and sysprof.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_preempt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_preempt.c

## Purpose

`a8xx_preempt.c` is the A8xx register variant of the A6xx preemption implementation. It reuses the shared preemption state machine and per-ring records but writes A8xx context-switch registers, keepalive register, and postamble performance-counter registers.

## Important APIs, Types, And Functions

Public functions are `a8xx_preempt_hw_init()`, `a8xx_preempt_trigger()`, and `a8xx_preempt_irq()`. Local helpers are `preempt_prepare_postamble()`, `preempt_disable_postamble()`, and `a8xx_preempt_keepalive_vote()`. It uses `try_preempt_state()`, `set_preempt_state()`, `update_wptr()`, and `get_next_ring()` from `a6xx_preempt.h`.

## Control Flow

`a8xx_preempt_hw_init()` skips single-ring GPUs, resets each preemption record's ring pointers, SMMU/ring metadata, writes zero to `REG_A8XX_CP_CONTEXT_SWITCH_SMMU_INFO`, enables GMEM save/restore, resets state, initializes `eval_lock`, and sets ring 0 as current.

`a8xx_preempt_trigger()` follows the same sequence as A6xx: claim `PREEMPT_NONE -> PREEMPT_START`, build context switch control with A8xx bitfields, choose the next non-empty ring, bail out with WPTR refresh when no switch is needed, update target SMMU info and record WPTR under ring lock, clear `restore_wptr`, vote A8xx preempt keepalive on, fenced-write A8xx SMMU and restore-record addresses, set `next_ring`, arm a 10-second timer, enable/disable postamble based on sysprof state, set `PREEMPT_TRIGGERED`, and fenced-write `REG_A8XX_CP_CONTEXT_SWITCH_CNTL`.

`a8xx_preempt_irq()` accepts only a triggered preemption, cancels the timer, checks `REG_A8XX_CP_CONTEXT_SWITCH_CNTL` STOP bit, queues recovery on failure, otherwise swaps `cur_ring`, clears `next_ring`, refreshes deferred WPTR, resets state, turns keepalive off, traces completion, and retriggers.

## State And Persistence Behavior

State is stored in shared `struct a6xx_gpu` fields: preemption records, SMMU info, current/next rings, postamble buffer, preempt timer, atomic preempt state, and flags for save/restore/GMEM. The keepalive vote persists in the A8xx GMU until explicitly cleared at IRQ completion or recovery.

## Dependencies And Integration Points

`a8xx_gpu.c` calls `a8xx_preempt_hw_init()` during hardware initialization, `a8xx_irq()` dispatches CP SW interrupts to `a8xx_preempt_irq()`, and retire/cache flush interrupts call `a8xx_preempt_trigger()`. Shared allocation for records is still handled by `a6xx_preempt_init()`, so A8xx depends on common preempt setup.

## Risks

This file is structurally duplicated from `a6xx_preempt.c`, so future bug fixes can diverge. A wrong generation-specific register or bitfield would break only A8xx context switches. There is no wrapper-GMU skip in `a8xx_preempt_keepalive_vote()`, unlike A6xx, so that assumption must match all A8xx supported devices. STOP-bit failure paths leave cleanup to recovery.

## Test Signals

Expected signals are normal CP SW completion interrupts, tracepoint trigger/IRQ pairs, no preemption watchdog timeouts, correct switching under multi-ring submissions, reliable sysprof postamble toggling with A8xx perf-counter registers, and successful recovery when STOP remains set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_device.c

## Purpose

`adreno_device.c` registers the Adreno platform driver, matches device-tree GPU nodes to catalog entries, binds the GPU into the MSM DRM component graph, loads firmware, initializes hardware under runtime PM, and implements system/runtime suspend and resume coordination.

## Important APIs, Types, And Functions

Module parameters are `hang_debug`, `snapshot_debugbus`, `enable_preemption`, `disable_acd`, and `no_gpu`/`skip_gpu`. Public entry points are `adreno_has_gpu()`, `adreno_load_gpu()`, `adreno_register()`, and `adreno_unregister()`. Driver callbacks include `adreno_probe()`, `adreno_remove()`, `adreno_shutdown()`, component `adreno_bind()`/`adreno_unbind()`, PM callbacks, and scheduler suspend/resume helpers. `adreno_info()` searches the family gpulists.

## Control Flow

`find_chipid()` first parses `compatible` strings in `qcom,adreno-XYZ.W`, `amd,imageon-XYZ.W`, or raw hex forms, then falls back to legacy `qcom,chipid`. `adreno_has_gpu()` honors `skip_gpu`, parses the chip ID, and checks that a matching catalog entry exists.

Probe either directly calls `msm_gpu_probe()` for imageon/no-components configurations or adds the device as a DRM component. Bind stores platform config, looks up `adreno_info`, sets private feature flags, calls the generation-specific `info->funcs->init()`, and discovers interconnect paths. `adreno_load_gpu()` loads firmware and optional microcode, enables runtime PM, powers the device, calls `msm_gpu_hw_init()` under `gpu->lock`, drops the autosuspend ref, and initializes debugfs when enabled.

System suspend stops all DRM scheduler workqueues, waits up to one second for `active_submits == 0`, then force-suspends runtime PM; on failure it restarts schedulers. System resume restarts schedulers after force resume. Runtime PM delegates to generation callbacks.

## State And Persistence Behavior

Persistent global/module state is held in module parameters. Per-device state is stored in static `adreno_platform_config config` inside bind, `priv->gpu_pdev`, `config.info`, `config.chip_id`, `priv->is_a2xx`, and `priv->has_cached_coherent`. Runtime PM state is enabled only after firmware is ready, and disabled on hardware-init failure.

## Dependencies And Integration Points

This file links all family catalog lists (`a2xx` through `a8xx`) and delegates real GPU behavior through `adreno_info->funcs`. It integrates with device tree, platform/component framework, DRM scheduler, runtime/system PM, OPP/interconnect lookup, firmware loading, debugfs, and module init/exit from the broader MSM DRM driver.

## Risks

The static `adreno_platform_config config` in `adreno_bind()` is shared storage and assumes one bound Adreno device. Chip-id parsing must remain compatible with old and new DT bindings. Suspend waits only one second for active submits; long-running jobs can block system suspend. `skip_gpu` disables registration globally. Firmware load failures abort GPU load before runtime PM setup, so error ordering matters.

## Test Signals

Signals include correct matching for each DT compatible form, successful bind/unbind, firmware and microcode load, hardware init under runtime PM, debugfs creation, clean runtime suspend with zero active submits, system suspend timeout behavior, and module parameter effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_0_0_snapshot.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_0_0_snapshot.h

## Purpose

`adreno_gen7_0_0_snapshot.h` is a static devcoredump register-capture description for Gen7 0.0 Adreno GPUs. It provides debugbus block IDs, shader memory block descriptors, GPU/GMU/register-range arrays, cluster capture tables, SPTP capture tables, and external core register lists consumed by the A6xx/A7xx GPU state snapshot code.

## Important APIs, Types, And Functions

The header exports data, not functions. Key symbols are `gen7_0_0_debugbus_blocks`, `gen7_0_0_shader_blocks`, pre/post crashdumper register arrays, `gen7_0_0_gpu_registers`, `gen7_0_0_gmu_registers`, `gen7_0_0_gmugx_registers`, non-context BR/BV/LPAC arrays, RB RAC/RBP selector structs, `gen7_0_0_clusters`, `gen7_0_0_sptp_clusters`, RSCC/CPR/GPUCC/CX_MISC/DPM arrays, `gen7_0_0_reg_list`, and `gen7_0_0_external_core_regs`.

## Control Flow

There is no executable control flow. Snapshot code iterates null- or sentinel-terminated tables. Register arrays encode inclusive start/end pairs terminated by `UINT_MAX, UINT_MAX`. Cluster arrays map cluster, pipe, forced-context state, register list, and optional selector register. SPTP arrays additionally specify SP/TP selector IDs, context indexes, logical locations such as HLSQ_STATE/SP_TOP/USPTP, and base offsets.

## State And Persistence Behavior

All data is `static const` and read-only after compilation. Captured state is generated at devcoredump time by consumers; this file only defines what hardware state should be sampled. `static_assert(IS_ALIGNED(sizeof(...), 8))` verifies register-pair alignment for snapshot iteration.

## Dependencies And Integration Points

The file includes `a6xx_gpu_state.h` for `gen7_*` table types and enum values. It depends on generated A7xx register/debugbus constants. It is integrated by device catalog or GPU-state selection paths that choose the appropriate snapshot tables for Gen7 0.0 hardware.

## Risks

Wrong register ranges can hang capture, miss diagnostic state, or read invalid/fused-off blocks. Selector register mistakes can capture the wrong RB/SP sub-block. The header is large and mostly declarative, so review should emphasize generated-data provenance, sentinel placement, alignment, and consistency with hardware manuals rather than local logic.

## Test Signals

Compile-time alignment asserts, successful devcoredump generation on Gen7 0.0 hardware, parseable debugbus sections, valid shader dumps, and no capture-time register read faults are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_0_0_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_2_0_snapshot.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_2_0_snapshot.h

## Purpose

`adreno_gen7_2_0_snapshot.h` defines devcoredump capture tables for Gen7 2.0 GPUs. It extends the Gen7 0.0 layout for a wider configuration: more debugbus blocks, 6-USP shader block dimensions, updated GPU/GMU/GMUGX ranges, DBGC capture, DPM leakage capture, and selective reuse of Gen7 0.0 register lists where hardware blocks match.

## Important APIs, Types, And Functions

Important symbols include `gen7_2_0_debugbus_blocks`, `gen7_2_0_shader_blocks`, `gen7_2_0_gpu_registers`, `gen7_2_0_gmu_registers`, `gen7_2_0_gmugx_registers`, non-context BR/BV and RB arrays, GRAS/RB/SP arrays, LPAC-specific SP arrays, selector structs, `gen7_2_0_clusters`, `gen7_2_0_sptp_clusters`, `gen7_2_0_dbgc_registers`, RSCC/CPR/DPM leakage/GPUCC/CX_MISC/DPM arrays, `gen7_2_0_reg_list`, and `gen7_2_0_external_core_regs`.

## Control Flow

The file has table-driven flow only. Consumers iterate `gen7_2_0_reg_list` for core GPU/CX/DPM/DBGC ranges, `gen7_2_0_external_core_regs` for external blocks, cluster tables for context-sensitive register blocks, and SPTP tables for shader/texture processor regions. Several cluster entries intentionally reference `gen7_0_0_*` arrays to avoid duplication when blocks are unchanged.

## State And Persistence Behavior

All state is immutable compile-time data. Arrays are terminated with `UINT_MAX` pairs and guarded by alignment asserts. The generated capture definitions persist in the kernel image and determine what state is captured during a GPU devcoredump.

## Dependencies And Integration Points

The header depends on `a6xx_gpu_state.h` and on Gen7 0.0 symbols being visible when this header is included in the same snapshot compilation unit. It integrates with catalog-selected snapshot descriptors and the A6xx/A7xx GPU-state dumper.

## Risks

Cross-version reuse is efficient but creates dependency risk: changing or removing a Gen7 0.0 symbol can break Gen7 2.0 capture. Mis-sized shader blocks or wrong USP counts can truncate or overrun diagnostic reads. DBGC and leakage ranges may be fuse or power-domain sensitive, so capture sequencing must match hardware availability.

## Test Signals

Build coverage should catch missing reused symbols and alignment failures. Hardware validation should confirm devcoredumps on Gen7 2.0 include DBGC, DPM leakage, shader blocks, core registers, external core registers, and cluster/SPTP sections without register access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_2_0_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_9_0_snapshot.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_9_0_snapshot.h

## Purpose

`adreno_gen7_9_0_snapshot.h` is the expanded devcoredump capture definition for Gen7 9.0 Adreno GPUs. It describes core, GMU, GMUGX, CX, DBGC, shader, cluster, SPTP, indexed CP, and external-core register captures, with generated comments documenting block grouping and register counts.

## Important APIs, Types, And Functions

Key symbols include `gen7_9_0_debugbus_blocks`, separate `gen7_9_0_gbif_debugbus_blocks` and `gen7_9_0_cx_debugbus_blocks`, `gen7_9_0_shader_blocks`, pre-crashdumper and core GPU/GMU/GMUGX/CX_MISC/DBGC/CX_DBGC arrays, non-context pipe arrays for BR/BV/LPAC, RB RAC/RBP arrays, GRAS/PC/VFD/VPC/RB/SP/TPL1 cluster arrays, selector structs, `gen7_9_0_clusters`, `gen7_9_0_sptp_clusters`, `gen7_9_0_cp_indexed_reg_list`, `gen7_9_0_reg_list`, and external CPR/DPM/DPM leakage/ACD/GPUCC/ISENSE/RSCC arrays.

## Control Flow

The file is entirely declarative. Snapshot consumers iterate sentinel-terminated register ranges and table arrays. Compared with earlier Gen7 snapshot headers, Gen7 9.0 splits debugbus capture into GPU, GBIF, and CX groups, adds HLSQ data-stripe and local-misc shader ranges, includes indexed CP registers through `struct a6xx_indexed_registers`, and carries many generated block comments with pair/register counts to support auditability.

## State And Persistence Behavior

The table data is immutable after compile. Register arrays use inclusive start/end pairs ending in `UINT_MAX, UINT_MAX`; alignment asserts protect the pair-walk ABI. Indexed register descriptors persist enough metadata for consumers to select indexed CP debug registers rather than plain address ranges.

## Dependencies And Integration Points

The header includes `a6xx_gpu_state.h`, depends on A7xx register/debugbus constants and snapshot table type definitions, and is selected by Gen7 9.0 catalog/state code for devcoredump capture. External core arrays require access to non-GPU register spaces such as CPR, DPM, GPUCC, ISENSE, and RSCC.

## Risks

The larger capture surface increases the chance of reading unavailable power domains or fused-off debug blocks. Indexed CP register capture has more sequencing risk than simple ranges. Generated table comments help audit pair counts, but stale generation input can still produce incomplete or unsafe ranges. Debugbus split groups must match the dumper's power/clock sequencing.

## Test Signals

Validation signals include successful compile-time alignment, devcoredump completion on Gen7 9.0 hardware, distinct GPU/GBIF/CX debugbus sections, usable indexed CP output, no external-core read faults, and enough SP/HLSQ/TPL1 state to diagnose shader hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_9_0_snapshot.h -->
