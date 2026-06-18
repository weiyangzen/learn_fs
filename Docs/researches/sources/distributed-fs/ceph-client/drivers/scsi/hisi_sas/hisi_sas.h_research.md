# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas.h

## Purpose

`hisi_sas.h` is the common private interface for the HiSilicon SAS HBA driver. It defines constants, host/phy/port/device/slot state, hardware-version callback operations, DMA memory layouts, debugfs capture structures, and exported common-core APIs.

## Important APIs, types, and data

- Global limits include max phys, queues, queue slots, ITCT/device entries, commands, reserved IPTT tags, CDB length, and block queue depth.
- `struct hisi_sas_phy`, `struct hisi_sas_port`, `struct hisi_sas_cq`, `struct hisi_sas_dq`, `struct hisi_sas_device`, and `struct hisi_sas_slot` model libsas phys/ports, hardware queues, devices, and in-flight commands.
- `struct hisi_sas_hw` is the hardware-version callback table for initialization, command preparation, PHY control, reset, ITCT setup/clear, debugfs snapshots, GPIO, and queue delivery.
- `struct hisi_hba` is the central host object, embedding `sas_ha_struct`, SCSI host pointer, MMIO bases, queue arrays, phy/port arrays, device table, DMA memory pointers, flags, workqueue, reset work, debugfs state, BIST state, and iopoll queue count.
- DMA ABI structures include command headers, ITCT, IOST, initial FIS, breakpoint buffers, SGE pages, command tables for SSP/SMP/STP, status buffers, and slot buffer tables.
- Address macros compute per-slot DMA and CPU addresses for status, command table, SGE, and DIF SGE buffers.
- Extern declarations expose common functions to hardware-specific source files.

## Control flow

Hardware-specific drivers allocate/populate `struct hisi_hba`, set a `struct hisi_sas_hw` table, and call common probe/allocation helpers. Common queue submission fills `struct hisi_sas_slot` and calls hardware callbacks to encode command headers. Completion and reset paths use shared state and hardware callbacks to recover, reinitialize, and notify libsas.

## State and persistence behavior

The header defines the persistent in-memory driver model. Device, slot, queue, debugfs, and DMA structures live for the HBA lifetime. Flags such as resetting, reject-command, PM, and hardware-fault persist across asynchronous work and error handling. Hardware-visible DMA tables persist until device removal or managed resource cleanup.

## Dependencies and integration points

The file includes ACPI, platform, PCI, libsas, libata, debugfs, DMA, blk-mq, runtime PM, regmap, and SCSI transport headers. It is the integration surface between `hisi_sas_main.c` and hardware version files.

## Risks and edge cases

- `struct hisi_hba` requires `struct sas_ha_struct *p` as the first element for `SHOST_TO_SAS_HA` usage; reordering would break conversions.
- `struct hisi_sas_slot` explicitly warns not to reorder members after `buf`; cleanup uses `offsetof(struct hisi_sas_slot, buf)`.
- Hardware callback availability varies by version; common code must check optional callbacks before calling.
- DMA layout structures are hardware ABI and must remain aligned and endian-correct.
- The debugfs arrays are large, especially at the maximum dump count.

## Test signals

Compile all hardware versions, validate structure sizes and alignments against hardware manuals, test DIF/DIX and non-protection allocations, verify reset flags and slot cleanup invariants, and exercise debugfs snapshot storage at configured dump counts.
