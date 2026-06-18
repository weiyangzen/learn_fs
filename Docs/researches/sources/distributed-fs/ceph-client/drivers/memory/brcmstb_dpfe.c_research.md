# sources/distributed-fs/ceph-client/drivers/memory/brcmstb_dpfe.c

## Purpose
`brcmstb_dpfe.c` is a Broadcom STB DDR PHY Front End platform driver. It loads or verifies firmware for a DCPU inside the DDR PHY, exchanges mailbox commands with that firmware, and exposes DRAM information such as refresh and mode-register data through sysfs.

## Important APIs, Types, And Functions
Important types are `struct dpfe_firmware_header`, temporary `struct init_data`, `struct dpfe_api`, and `struct brcmstb_dpfe_priv`. API tables describe legacy v2, new v2, and v3 command layouts and sysfs attribute groups. Core functions include DCPU enable/disable helpers, `__send_command()`, firmware verification/write/checksum helpers, `brcmstb_dpfe_download_firmware()`, sysfs show/store methods, `brcmstb_dpfe_probe()`, remove, and resume.

## Control Flow
Probe maps named resources `dpfe-cpu`, `dpfe-dmem`, and `dpfe-imem`, selects the API table from OF match data, downloads firmware if needed, and creates API-specific sysfs groups. Firmware download first checks whether a running DCPU responds to GET_INFO. If not and a firmware filename is available, it requests firmware, validates magic, endian, sizes, and checksum, disables the DCPU, clears and writes DMEM/IMEM, verifies by reading back, then enables the DCPU. Sysfs reads send commands through message RAM and mailboxes, validate response checksums, then format version, refresh, vendor, or v3 DRAM data.

## State And Persistence
Driver state holds MMIO bases, selected API, device pointer, and a mutex. Hardware state includes DCPU reset/clock bits, mailbox registers, message RAM, DCPU IMEM/DMEM, and firmware execution state. Sysfs writes to `dpfe_refresh` update the firmware-provided interval field for API v2-style data. Resume reruns firmware download/verification.

## Dependencies And Integration Points
The driver depends on platform resources, OF match data, firmware loader, relaxed MMIO accessors, sysfs device attributes, mutex serialization, and Broadcom-compatible strings. It is built from `CONFIG_BRCMSTB_DPFE` and uses firmware `dpfe.bin` only for the old API path; newer APIs expect boot firmware to preload DCPU firmware.

## Risks And Test Signals
Risks include mailbox timeout handling, checksum index trust from firmware responses, endian conversion mistakes, firmware blob layout mismatches, stale DCPU firmware on resume, invalid response pointers for old APIs, and sysfs writes racing with reads. Tests should cover all OF compatibles/API tables, missing resources, missing firmware with probe defer, BE and LE firmware images, invalid magic/size/checksum, mailbox timeout/error codes, sysfs output formatting for v2 and v3, refresh writes, remove cleanup, and resume after DCPU reset.
# sources/distributed-fs/ceph-client/drivers/memory/brcmstb_dpfe.c

## Purpose
`brcmstb_dpfe.c` is a Broadcom STB DDR PHY Front End platform driver. It loads or verifies firmware for a DCPU inside the DDR PHY, exchanges mailbox commands with that firmware, and exposes DRAM information such as refresh and mode-register data through sysfs.

## Important APIs, Types, And Functions
Important types are `struct dpfe_firmware_header`, temporary `struct init_data`, `struct dpfe_api`, and `struct brcmstb_dpfe_priv`. API tables describe legacy v2, new v2, and v3 command layouts and sysfs attribute groups. Core functions include DCPU enable/disable helpers, `__send_command()`, firmware verification/write/checksum helpers, `brcmstb_dpfe_download_firmware()`, sysfs show/store methods, `brcmstb_dpfe_probe()`, remove, and resume.

## Control Flow
Probe maps named resources `dpfe-cpu`, `dpfe-dmem`, and `dpfe-imem`, selects the API table from OF match data, downloads firmware if needed, and creates API-specific sysfs groups. Firmware download first checks whether a running DCPU responds to GET_INFO. If not and a firmware filename is available, it requests firmware, validates magic, endian, sizes, and checksum, disables the DCPU, clears and writes DMEM/IMEM, verifies by reading back, then enables the DCPU. Sysfs reads send commands through message RAM and mailboxes, validate response checksums, then format version, refresh, vendor, or v3 DRAM data.

## State And Persistence
Driver state holds MMIO bases, selected API, device pointer, and a mutex. Hardware state includes DCPU reset/clock bits, mailbox registers, message RAM, DCPU IMEM/DMEM, and firmware execution state. Sysfs writes to `dpfe_refresh` update the firmware-provided interval field for API v2-style data. Resume reruns firmware download/verification.

## Dependencies And Integration Points
The driver depends on platform resources, OF match data, firmware loader, relaxed MMIO accessors, sysfs device attributes, mutex serialization, and Broadcom-compatible strings. It is built from `CONFIG_BRCMSTB_DPFE` and uses firmware `dpfe.bin` only for the old API path; newer APIs expect boot firmware to preload DCPU firmware.

## Risks And Test Signals
Risks include mailbox timeout handling, checksum index trust from firmware responses, endian conversion mistakes, firmware blob layout mismatches, stale DCPU firmware on resume, invalid response pointers for old APIs, and sysfs writes racing with reads. Tests should cover all OF compatibles/API tables, missing resources, missing firmware with probe defer, BE and LE firmware images, invalid magic/size/checksum, mailbox timeout/error codes, sysfs output formatting for v2 and v3, refresh writes, remove cleanup, and resume after DCPU reset.
