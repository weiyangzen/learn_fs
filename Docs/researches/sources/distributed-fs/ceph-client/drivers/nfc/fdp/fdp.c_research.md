# sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.c

Purpose: Implements the Intel Fields Peak NFC core NCI driver. It registers an `nci_dev`, controls open/send/setup/post-setup operations, applies OTP/RAM firmware patches through proprietary NCI commands and data connections, parses version/config responses, and exports probe/remove for physical transports.

Important APIs, types, and functions: `struct fdp_nci_info` holds transport, firmware, version, clock, wait-queue, and patch state. `fdp_nci_probe()` allocates/registers the NCI device; `fdp_nci_setup()` initializes NCI, loads firmware, compares versions, applies OTP/RAM patches, verifies versions, and resets; `fdp_nci_post_setup()` sends vendor production data and clock settings; `fdp_nci_send_patch()` segments firmware manually; `fdp_core_ops` and `fdp_prop_ops` register response/notification handlers.

Control flow: Transport probe calls `fdp_nci_probe()`. On NCI setup, the driver initializes the core, requests firmware files, creates a proprietary patch connection when needed, sends patch chunks as data packets, waits until all packets are physically sent, closes the data connection, sends end-of-transfer, waits for patch and reset notifications, then reinitializes and verifies firmware versions. Normal sends decrement the data packet counter before writing through `phy_ops`.

State and persistence behavior: Firmware blobs are transient `request_firmware()` references. Version numbers, key index, setup flags, patch status, data packet counter, wait queue, clock configuration, and transport pointer live in `fdp_nci_info`. Actual firmware persistence is in the NFC controller, not the driver.

Dependencies and integration points: Uses Linux firmware loading, NFC NCI core/proprietary command APIs, wait queues, atomics, and transport `nfc_phy_ops` supplied by `fdp/i2c.c`.

Risks: Firmware header offsets are assumed valid; short firmware files could read beyond data. Waits are interruptible but return values are not always checked, so interrupted setup could continue with stale flags. Data-packet callback ordering is critical because end-of-transfer must follow the last physical I2C write. Proprietary response parsers trust minimum payload lengths.

Test signals: Probe/register/remove, missing RAM or OTP firmware, older/equal/newer firmware versions, patch notification and reset notification ordering, interrupted waits, short/corrupt firmware files, clock/VSC property variants, NCI command failures, and data send/write failures.
