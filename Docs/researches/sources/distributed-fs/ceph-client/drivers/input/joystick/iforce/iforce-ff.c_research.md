# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-ff.c

Purpose: Force-feedback effect encoder for I-Force devices. It converts Linux `struct ff_effect` periodic, constant, spring, and damper effects into I-Force command packets and manages on-device effect parameter memory.

Important APIs/types/functions: Modifier builders include `make_magnitude_modifier()`, `make_period_modifier()`, `make_envelope_modifier()`, and `make_condition_modifier()`. Change detectors include `need_*_modifier()` and `need_core()`. `make_core()` sends the common effect core packet and restarts effects if requested. Public upload functions are `iforce_upload_periodic()`, `iforce_upload_constant()`, and `iforce_upload_condition()`.

Control flow: The input FF upload callback in `iforce-main.c` dispatches to one of these upload functions. Each upload function allocates or reuses resource chunks for needed modifiers, sends modifier packets, sets `FF_MOD*_IS_USED`, sends a core packet when core fields changed, and returns 0 for sent updates, 1 for no change, or a negative error.

State and persistence: Uses `iforce->device_memory` resource tree and each `core_effects[id]` resource/flag set. `mem_mutex` protects resource allocation and release. State persists while the input FF effect exists, then is freed by erase in `iforce-main.c`; no disk persistence.

Dependencies and integration points: Shared `iforce.h`, input FF effect structures, Linux resource allocator, I-Force command IDs, and `iforce_send_packet()`.

Risks: The file comments call out arithmetic right-shift assumptions in condition scaling. Resource allocation sizes and device memory limits can reject complex effects with `-ENOSPC`. Some unsupported condition types return `-1` rather than a specific errno. Effect replay count is not preserved when restarting after update.

Test signals: Upload/update/no-change for periodic waveforms, constant effects, spring/damper condition effects, envelope-only changes, memory exhaustion, erase/reupload cycles, and packet bytes for boundary magnitudes including values near `0x80`.
