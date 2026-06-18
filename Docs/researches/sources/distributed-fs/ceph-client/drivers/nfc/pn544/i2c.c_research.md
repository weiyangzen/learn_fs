# sources/distributed-fs/ceph-client/drivers/nfc/pn544/i2c.c

Purpose: Implements the PN544 HCI-over-I2C transport, SHDLC-style length/CRC framing, GPIO power/mode control, IRQ RX dispatch, and I2C firmware download for C2/C3 hardware variants.

Important APIs and functions: `struct pn544_i2c_phy` stores I2C client, HCI device, enable/firmware GPIOs, polarity, hardware variant, firmware worker state, firmware pointers/counters, powered/run mode, and hard fault. PHY ops are `pn544_hci_i2c_write()`, `pn544_hci_i2c_enable()`, and `pn544_hci_i2c_disable()`. Firmware helpers include `pn544_hci_i2c_fw_download()`, `pn544_hci_i2c_fw_work()`, `pn544_hci_i2c_fw_write_cmd()`, `pn544_hci_i2c_fw_check_cmd()`, and secure-write helpers.

Control flow: Probe maps ACPI GPIOs, gets enable/firmware GPIOs, detects enable polarity by trying reset commands, requests a rising IRQ, and calls `pn544_hci_probe()` with SHDLC LLC and firmware-download callback. HCI writes push a length byte and CRC, retry standby `-EREMOTEIO`, then restore the SKB. IRQ dispatch reads firmware status in FW mode or validates length/CRC and sends HCI frames to `nfc_hci_recv_frame()` in HCI mode. Firmware download schedules a worker that enters FW mode, requests firmware, writes/checks legacy C2 blobs or secure C3 frames/chunks, and completes through `nfc_fw_download_done()`.

State and persistence: Runtime state includes GPIO power/run mode, hard fault, firmware progress fields, work state, and HCI device pointer. Firmware file contents are transient.

Dependencies and integration points: Uses I2C, GPIO, ACPI/OF matching, CRC-CCITT, NFC HCI/LLC SHDLC, firmware API, and PN544 core probe/remove.

Risks: CRC/length recovery flushes the bus based on assumptions about one frame per interrupt. Polarity auto-detect can fail and falls back active high. Firmware worker mixes IRQ-completed statuses and scheduled work; remove must complete in-progress downloads. Test signals include polarity detection, HCI CRC error flush, standby retry, hard fault, FW C2 write/check sequence, FW C3 secure chunking/reset, IRQ mode switch, and remove during download.
