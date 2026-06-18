# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.c

## Purpose
Implements Intel Xe GSC firmware lifecycle for the media GT: firmware staging into a private stolen-memory BO, GSCCS command submission for firmware load, compatibility-version query, async work handling, GSC reset workarounds, HuC-after-GSC authentication, proxy startup, and diagnostic printing.

## Important APIs, Types, and Functions
- Public entry points: `xe_gsc_init`, `xe_gsc_init_post_hwconfig`, `xe_gsc_load_start`, `xe_gsc_wait_for_worker_completion`, `xe_gsc_stop_prepare`, `xe_gsc_hwe_irq_handler`, `xe_gsc_wa_14015076503`, and `xe_gsc_print_info`.
- Firmware load helpers: `memcpy_fw`, `emit_gsc_upload`, `gsc_fw_is_loaded`, `gsc_fw_wait`, `gsc_upload`, and `gsc_upload_and_init`.
- Version query path uses `xe_gsc_emit_header`, `xe_gsc_pkt_submit_kernel`, and `xe_gsc_read_out_header` with MKHI compatibility-version ABI structures.
- Async work is encoded in `gsc->work_actions` using `GSC_ACTION_FW_LOAD`, `GSC_ACTION_SW_PROXY`, and `GSC_ACTION_ER_COMPLETE`, then consumed by `gsc_work`.

## Control Flow
- `xe_gsc_init` marks the GSC firmware type, initializes work/lock state, rejects non-media GTs when a media GT exists, initializes the uC firmware object, and initializes the GSC proxy unless the platform/configuration makes it unavailable.
- `xe_gsc_init_post_hwconfig` allocates a 4 MiB stolen/GGTT private BO, creates a permanent kernel GSCCS exec queue, creates an ordered workqueue, and marks the firmware loadable.
- `xe_gsc_load_start` handles already-loaded firmware surviving GT reset/D3Hot, otherwise sets `GSC_ACTION_FW_LOAD` and queues work.
- `gsc_upload_and_init` applies workaround `14018094691` with forcewake/MCR writes around `gsc_upload`, marks firmware transferred/running, restores sanitized frequencies, attempts HuC auth through GSC, and starts the GSC proxy.
- `xe_gsc_hwe_irq_handler` queues `GSC_ACTION_ER_COMPLETE`; `gsc_er_complete` reads `GSCI_TIMER_STATUS` and wedges the device if the Xe2 GSC engine reset timer expired.

## State and Persistence
- Persistent driver state lives in `struct xe_gsc`: firmware status, private BO, exec queue, ordered workqueue, pending action bits, and proxy state.
- GSC firmware survives GT reset and D3Hot; the code detects loaded firmware and only redoes missing proxy initialization state.
- `xe->needs_flr_on_fini` is set after firmware upload because the GSC can keep using the assigned memory until an FLR/D3cold-style reset.
- Firmware status transitions include loadable, transferred, running, and load-fail through `xe_uc_fw_change_status`.

## Dependencies and Integration Points
- Depends on Xe BO/GGTT mapping, GSCCS batch-buffer submission, uC firmware management, forcewake, MCR, GuC PC frequency control, HuC auth, proxy code, and GSC/HW registers.
- Integrated into GT init via `xe_uc_init_post_hwconfig`/GSC uC flows and GT reset via `xe_gsc_wa_14015076503`.
- `xe_gsc_print_info` is exposed by GSC debugfs and reads HECI status registers under `XE_FW_GSC` forcewake.

## Risks and Edge Cases
- Firmware copy uses CPU memcpy as a workaround for stolen-memory migration limitations, so mapping lifetime and BO size assumptions are important.
- Firmware load and packet submit both wait only one second for fences; slow GSCCS execution can produce `-ETIME`.
- Missing proxy completion before stop is treated seriously because interrupted init requires FLR to recover.
- Reset-timer failure currently wedges the full device because runtime FLR recovery is not implemented.

## Test Signals
- Boot/probe with GSC-capable media GTs should log GSC compatibility version and transition firmware to running.
- debugfs `gsc_info` should show firmware and HECI FWSTS values.
- Reset tests should cover GSC-loaded and GSC-not-loaded paths, including workaround register toggling.
- HuC authentication via GSC and MEI proxy startup are high-value integration signals.
