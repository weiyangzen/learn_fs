# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evgpe.c

## Purpose
Implements General Purpose Event runtime control, detection, and dispatch. It tracks runtime enable references and masks, maps raw GPE numbers to event descriptors, scans interrupt blocks, atomically detects enabled status bits, dispatches raw/normal handlers, queues methods or implicit notifies, and finishes GPEs with correct edge/level clear timing.

## Important APIs, Types, And Functions
- `acpi_ev_update_gpe_enable_mask`, `acpi_ev_enable_gpe`, `acpi_ev_mask_gpe`, `acpi_ev_add_gpe_reference`, and `acpi_ev_remove_gpe_reference` maintain runtime enable state and hardware enable bits.
- `acpi_ev_low_get_gpe_info` and `acpi_ev_get_gpe_event_info` resolve raw GPE numbers within FADT or device GPE blocks.
- `acpi_ev_gpe_detect` scans all blocks on an interrupt descriptor and delegates each bit to `acpi_ev_detect_gpe`.
- `acpi_ev_detect_gpe` reads enable/status registers, invokes the global event handler, and dispatches active GPEs.
- `acpi_ev_gpe_dispatch`, `acpi_ev_asynch_execute_gpe_method`, `acpi_ev_asynch_enable_gpe`, and `acpi_ev_finish_gpe` handle disable/clear/execute/re-enable sequencing.

## Control Flow
Runtime references set `enable_for_run` and enable hardware on the first reference; the last reference clears the mask and disables hardware. Interrupt scanning skips registers with no run or wake enables. Each candidate GPE is detected under `acpi_gbl_gpe_lock`, but the block scan releases the lock around per-GPE detection to reduce critical sections. Active raw handlers run with the GPE lock released. Standard dispatch first disables the GPE, clears edge-triggered status before service, then invokes an interrupt-level handler, queues a method/notify worker, or leaves unhandled GPEs disabled. Method/notify completion defers re-enable until notify handlers can complete, and level-triggered status is cleared in `acpi_ev_finish_gpe`.

## State And Persistence
Per-GPE state includes `runtime_count`, `flags`, `disable_for_dispatch`, `dispatch.handler`, `dispatch.method_node`, `dispatch.notify_list`, and register masks `enable_for_run`, `enable_for_wake`, `mask_for_run`, and `enable_mask`. Global counters include `acpi_gpe_count`; global event handlers receive each active GPE.

## Dependencies And Integration Points
Depends on GPE block metadata, hardware GPE read/write helpers, OS lock and work-queue execution, namespace method evaluation, notify queuing, and global event handler callbacks. It integrates with public GPE enable/mask APIs and with `_Lxx`/`_Exx` discovery from `evgpeinit.c`.

## Risks And Edge Cases
Reference count overflow/underflow returns `AE_LIMIT`. Mask/unmask validates current mask state and can reject duplicate operations. Raw handler safety depends on caller-installed handler lifetime and flushing before destruction. Failed queueing leaves the event disabled after logging. Edge and level clear timing must not be swapped or GPEs can be lost or storm.

## Test Signals
Signals include first/last reference hardware enable transitions, duplicate mask/unmask errors, lookup across GPE0/GPE1 and device GPE blocks, skipped disabled registers, global handler calls, raw handler execution with lock released, edge GPE status cleared before handler, level GPE status cleared after completion, and method/notify dispatch re-enabling only after finish.
