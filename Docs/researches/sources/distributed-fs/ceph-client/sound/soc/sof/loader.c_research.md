# sources/distributed-fs/ceph-client/sound/soc/sof/loader.c

Purpose: Provides generic SOF firmware loading and run sequencing shared by platform drivers. It requests the base firmware, handles extended-manifest offseting, validates and copies firmware to DSP memory, starts the DSP, waits for firmware-ready, and releases the base firmware.

Important APIs and state: `snd_sof_load_firmware_raw()` populates `sdev->basefw.fw` and `basefw.payload_offset`. `snd_sof_load_firmware_memcpy()` validates through IPC-specific loader ops, resets the DSP, and calls `load_fw_to_dsp`. `snd_sof_run_firmware()` initializes `boot_wait`, creates first-boot debugfs firmware version storage, runs platform pre/run/post callbacks, waits on `sdev->fw_state`, and marks `SOF_FW_BOOT_COMPLETE`. `snd_sof_fw_unload()` releases `basefw.fw`.

Control flow: raw load builds `fw_path/fw_filename`, calls `request_firmware()`, then lets `fw_loader->parse_ext_manifest()` decide whether to skip an extended manifest. memcpy load calls raw load, validates the SOF firmware header, resets the DSP, and invokes the IPC loader's load path. run firmware resets dump flags, calls `snd_sof_dsp_pre_fw_run()`, starts the DSP with `snd_sof_dsp_run()`, waits up to `boot_timeout` for state to move past `SOF_FW_BOOT_IN_PROGRESS`, handles ready failure or timeout dumps, performs post-run, then IPC post-boot.

Dependencies and integration: Uses `sdev->ipc->ops->fw_loader` for manifest parsing, validation, and DSP load; `ops.h` for DSP reset/run/pre/post wrappers; SOF debugfs and firmware state helpers; platform probe paths choose this loader via `.load_firmware`.

Risks: The firmware pointer is cached, so callers must release on validation/load errors to avoid stale state. Boot wait depends on asynchronous IPC RX updating `fw_state`; missing mailbox IRQs surface as generic `-EIO`. Manifest offset errors corrupt firmware load addresses. Debugfs creation is fatal on allocation failure during first boot.

Test signals: Missing firmware, invalid extended manifest, invalid SOF header, DSP reset failure, loader failure cleanup, boot timeout, FW_READY failure, post-fw-run failure, IPC post-boot failure, and successful unload/reload across suspend.
