# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/i2c.c

## Purpose
`i2c.c` is the ST21NFCA I2C physical layer and HCI LLC framing implementation. It handles enable GPIO, proprietary reboot, byte-stuffed SOF/EOF framing, CRC-CCITT, IRQ-driven multi-read receive assembly, and registration of the HCI core over SHDLC.

## Important APIs, types, and functions
- `struct st21nfca_i2c_phy` stores I2C client, HCI device, enable GPIO, SE status, pending receive skb, read sequence state, CRC retry count, power/run state, hard fault, and a bus mutex.
- `st21nfca_hci_platform_init()` sends a proprietary reboot command and waits for fill bytes.
- `st21nfca_hci_i2c_write()` adds length/CRC, SOF/EOF, byte stuffing, retries I2C writes, and restores the skb before returning.
- `st21nfca_hci_i2c_read()` reads variable chunks from `len_seq` until EOF, handles repeated SOF, and calls repack.
- `st21nfca_hci_i2c_repack()` removes byte stuffing, validates CRC, strips header/CRC, and returns the LLC payload size.
- IRQ thread reads/retries frames and calls `nfc_hci_recv_frame()`.

## Control flow
Probe allocates the physical object and pending skb, gets enable GPIO, reads SE properties, reboots the chip, registers IRQ, and calls `st21nfca_hci_probe()` with `LLC_SHDLC_NAME` and frame headroom/tailroom. On write, the NFC HCI core supplies an skb that is temporarily modified for wire encoding then restored. On IRQ, the driver accumulates chunks of 16, 24, 12, and 29 bytes until an EOF byte is seen; valid frames are delivered to HCI, incomplete frames await more IRQs, CRC errors retry a bounded number of times, and fatal errors notify HCI with NULL.

## State and persistence
Runtime state includes power/run mode, current read length index, CRC trial count, pending skb, hard-fault latch, and GPIO level. Persistent inputs are ACPI/OF properties and no data is written.

## Dependencies and integration points
The file depends on I2C, GPIO, ACPI/OF, IRQs, CRC-CCITT, firmware headers, NFC HCI/LLC/SHDLC, and the ST21NFCA core. Compatible strings include `st,st21nfca-i2c` and `st,st21nfca_i2c`; ACPI ID is `SMO2100`.

## Risks
Write mutates the caller skb while encoding and assumes `st21nfca_hci_remove_len_crc()` fully restores it. Byte unstuffing uses index arithmetic that must be robust against malformed escape-at-end frames. CRC error retry frees/reallocates pending skbs; allocation failure creates a hard fault. The protocol has no explicit length field, so sync recovery depends on SOF/EOF and fixed read sequences.

## Test signals
Test platform reboot success/failure, write byte-stuffing and CRC restoration, read chunk sequencing, repeated SOF resynchronization, CRC retry exhaustion, hard fault on I2C error/allocation failure, SE property propagation, and remove while powered.
