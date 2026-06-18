<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c

Purpose: Implements the USB frontend for AR9170/carl9170 devices: device ID matching, firmware loading, URB pools, command transport, RX/TX completion paths, restart/reset handling, probe/disconnect, and PM resume.

Important APIs/types/functions: Registers `carl9170_driver` through `module_usb_driver()`. Exports driver-facing functions such as `carl9170_exec_cmd()`, `__carl9170_exec_cmd()`, `carl9170_usb_tx()`, `carl9170_usb_open()`, `carl9170_usb_stop()`, `carl9170_usb_restart()`, `carl9170_usb_reset()`, and `carl9170_usb_handle_tx_err()`. Probe/firmware callbacks include `carl9170_usb_probe()`, `carl9170_usb_firmware_step2()`, `carl9170_usb_firmware_finish()`, and `carl9170_usb_disconnect()`.

Control flow: Probe resets the device, allocates `struct ar9170`, validates endpoints, initializes anchors/completions/tasklet state, and asynchronously requests firmware. Firmware finish parses metadata, starts interrupt and bulk RX URBs, uploads firmware by control transfers, waits for boot completion, runs echo test, registers mac80211, then stops until opened. RX bulk completions move URBs to a work anchor and schedule the high-priority tasklet, which calls `carl9170_rx()` and the TX scheduler. TX submissions are anchored in wait/active/error lists; completions either call `carl9170_tx_callback()` or defer failures to tasklet cleanup. Commands use a single in-flight command URB path plus completion waiting in `carl9170_exec_cmd()`.

State and persistence: Maintains USB anchors, URB counters, command response buffers/lengths, boot/load completions, endpoint mode, firmware pointer/parsed metadata, and carl9170 state transitions. No persistent storage beyond firmware image ownership.

Dependencies and integration points: Uses Linux USB core, firmware loader, mac80211 registration, carl9170 firmware command/RX/TX layers, tasklets, completions, and PM callbacks.

Risks and test signals: Risks include command timeouts forcing restarts, RX URB starvation, tasklet/anchor lifetime during disconnect, endpoint shape differences between full/high speed, and reset/resume losing mac80211 state. Test signals are probe with supported IDs, firmware upload and boot response, command echo, RX/TX stress, disconnect during traffic, suspend/resume, and firmware restart recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c -->
