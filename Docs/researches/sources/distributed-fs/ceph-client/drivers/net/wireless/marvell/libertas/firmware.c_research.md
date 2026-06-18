## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/firmware.c

Purpose: this file loads Libertas firmware by card model, supporting both async and legacy synchronous APIs and both one-stage helper-only and two-stage helper-plus-main firmware arrangements.

Important functions: `lbs_get_firmware_async()` records device, model, firmware table, callback, and starts table iteration. `load_next_firmware_from_table()` skips non-matching models, releases stale helper firmware, and requests the next helper. `helper_firmware_cb()` either requests the main firmware or reports helper-only success. `main_firmware_cb()` reports two-stage success. `lbs_fw_loaded()` calls the bus/core callback, clears `fw_callback`, and wakes `fw_waitq`. `lbs_wait_for_firmware_load()` waits for async completion. `lbs_get_firmware()` is the deprecated synchronous table-search equivalent.

Control flow: async loading uses `request_firmware_nowait()` for helper and optional main firmware. Missing firmware advances to the next table entry until a null helper terminator produces `-ENOENT`. Success passes firmware pointers to the caller callback; this file releases references after callback in the async path, so consumers must use them during callback or take their own references according to the surrounding driver contract.

State and persistence: `lbs_private` stores `fw_device`, `fw_table`, `fw_iter`, `fw_model`, `helper_fw`, and `fw_callback`. Firmware objects are kernel firmware references and not persisted by this file.

Dependencies and integration: bus drivers provide firmware tables and callbacks; core shutdown can wait for completion. The firmware loader subsystem and module reference handling are central dependencies.

Risks and tests: callback lifetime is subtle because async callbacks release firmware after notifying. Table iteration must avoid mismatched helper/main pairs and release helper on failure. Test signals include missing helper fallback, one-stage devices, two-stage devices, concurrent async call returning `-EBUSY`, wait completion, and synchronous fallback cleanup.
