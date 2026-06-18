# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.c

## Purpose

`amdgpu_ras_process.c` coordinates asynchronous RAS event processing around interrupts, bad-page retirement, poison consumption, and GPU reset pause/resume.

## Important APIs, Types, And Functions

Public functions initialize/finalize processing, handle UMC, unexpected, and consumption interrupts, bracket event processing with `amdgpu_ras_process_begin/end`, and run pre/post reset hooks. The delayed work function `ras_process_retire_page_dwork` periodically calls `ras_umc_handle_bad_pages`.

## Control Flow, State, And Persistence

Init clears `is_paused`, initializes a completion, and sets up delayed work. The work item skips RMA devices, delays if reset or recovery is active, otherwise retires bad pages and reschedules every 100 ms on success. UMC interrupts enqueue rascore processing as poison creation. Unexpected interrupts mark FED and request a mode1 GPU reset. Consumption interrupts either invoke VF poison handler or build a `ras_event_req`, obtain a poison-consumption seqno while filtering duplicate stale seqnos, and enqueue processing. Pre-reset pauses new processing, waits up to 1200 ms for current event completion, and flushes retirement work; post-reset resumes and schedules work.

## Dependencies And Integration Points

It depends on the RAS manager context, rascore process queue, UMC bad-page handling, AMDGPU reset/recovery state, SR-IOV poison hooks, and sequence-number FIFOs.

## Risks And Test Signals

Risks include delayed work running after teardown, completion timeout during reset, duplicate or stale poison sequence numbers, missed VF poison callbacks, and bad-page retirement rescheduling too aggressively. Test signals include interrupt enqueue tests, reset while RAS events are active, RMA skip behavior, delayed-work cancellation at fini, VF poison handling, and duplicate seqno handling.
