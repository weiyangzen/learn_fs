# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_ccg.c

Purpose: Implements UCSI support for Cypress CCGx Type-C controllers over I2C, including HPI register access, interrupt-to-UCSI op-region caching, NVIDIA altmode quirks, runtime PM, optional firmware update from CYACD images, and sysfs-triggered flashing.

Important APIs/types/functions: `struct ucsi_ccg` stores device/client, UCSI core, firmware/version info, HPI response state, IRQ/work, locks, NVIDIA altmode mapping arrays, spin-protected op-region cache, and PM workaround work. Key functions include `ccg_read/write`, `ccg_op_region_update`, `ucsi_ccg_init`, `ucsi_ccg_sync_control`, `ccg_irq_handler`, `ccg_send_command`, firmware command helpers, `ccg_fw_update_needed`, `do_flash`, `ccg_fw_update`, `ccg_restart`, `ucsi_ccg_probe/remove`, and PM callbacks.

Control flow and state: probe initializes locks/work, reads firmware-name to select NVIDIA build quirks, starts UCSI mode in the CCG controller, reads firmware/device info, creates UCSI with `ucsi_ccg_ops`, requests IRQ, registers UCSI, and enables autosuspend. IRQ handling reads the CCG interrupt register, reads UCSI CCI, copies CCI/message-in into `op_data` before clearing interrupt, then calls `ucsi_notify_common`. Sync control serializes with `uc->lock`, handles multiple-DP CAM remapping, delegates to common UCSI sync, and post-processes GET_CURRENT_CAM, GET_ALTERNATE_MODES, and GET_CAPABILITY for NVIDIA quirks.

Persistence behavior: in-memory state includes cached op-region, firmware versions, altmode remap tables, command response flags, and runtime PM state. Firmware flashing persists to the controller: signed FW config table/signature rows and CYACD rows are written, validated, reset, and ports re-enabled.

Dependencies/integration points: I2C transfer APIs, runtime PM, firmware loader, hex parser, sysfs device attribute `do_flash`, UCSI core, Type-C DP helpers, ACPI/OF/I2C matching, threaded IRQ, and NVIDIA-specific firmware naming conventions.

Risks: firmware update is high blast-radius: bad image format, wrong vendor/build, interrupted flashing, or row-write failure can affect controller bootability. The code must hold `uc->lock` around HPI commands and `op_lock` around cached CCI/message data. Multiple-DP altmode squashing and CAM remapping are subtle and partner-pin-dependent. Runtime resume works around old NVIDIA firmware by manually invoking IRQ handling. `ccg_read/write` use runtime PM around each transfer and need correct adapter quirks handling.

Test signals: I2C read/write success under adapter max-read constraints, UCSI init/start/stop, IRQ CCI/message caching before interrupt clear, NVIDIA multi-DP altmode discovery and `SET_NEW_CAM` remap, Tegra capability masking, runtime resume workaround on old firmware, sysfs `do_flash` with signed/unsigned CYACD images, validation/reset/port re-enable after flash, and remove during pending work.
