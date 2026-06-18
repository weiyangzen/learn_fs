# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/firmware.c

Purpose: Implements NXP NCI firmware download framing, CRC, command-response handling, asynchronous work progression, and firmware completion.

Important APIs and functions: Public functions are `nxp_nci_fw_download()`, `nxp_nci_fw_work()`, `nxp_nci_fw_recv_frame()`, and `nxp_nci_fw_work_complete()`. Helpers include `nxp_nci_fw_crc()`, `nxp_nci_fw_send_chunk()`, `nxp_nci_fw_send()`, `nxp_nci_fw_read_status()`, and `nxp_nci_fw_check_crc()`.

Control flow: Download validates transport support and firmware name, requests the firmware, switches the PHY to firmware mode, initializes pointers/counters, and schedules work. The worker sends one firmware frame at a time, splitting it into payload-size chunks with a big-endian length header, chunk flag, and custom CRC. Non-reset commands wait up to 30 seconds for `cmd_completion`, which is completed by IRQ-side `nxp_nci_fw_recv_frame()`. On response, CRC and status are decoded, then the worker advances to the next chunk/frame or completes the download.

State and persistence: `nxp_nci_fw_info` stores firmware name/pointer, remaining size, current data pointer, frame size, written bytes, work item, completion, and command result. Firmware contents are transient and released at completion.

Dependencies and integration points: Uses request_firmware, NCI SKB allocation, unaligned big-endian helpers, PHY `set_mode()`/`write()`, and `nfc_fw_download_done()`.

Risks: Firmware frame sizes are trusted after checking against remaining firmware size. Completion can be interrupted or time out. Status mapping is device-specific and some statuses become non-obvious Linux errors. Test signals include reset frame behavior, multi-chunk frames, CRC mismatch, status error mapping, timeout, interrupted wait, write failure, remove during download, and max-payload boundary cases.
