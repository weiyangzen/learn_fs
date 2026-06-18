# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_synquacer.c

## Purpose
Provides a Socionext SynQuacer MMIO TPM front-end for the generic TIS core, using byte-wise 16/32-bit accesses required by the platform controller.

## Important APIs, Types, And Functions
Defines `struct tpm_tis_synquacer_info` and `struct tpm_tis_synquacer_phy`. PHY ops are `tpm_tis_synquacer_read_bytes()` and `tpm_tis_synquacer_write_bytes()`, wired through `tpm_tcg_bw`. Probe and init are `tpm_tis_synquacer_probe()` and `tpm_tis_synquacer_init()`.

## Control Flow
Probe obtains the MMIO resource, disables IRQ support by setting `irq = -1`, maps the resource, and calls `tpm_tis_core_init()`. Read operations perform byte reads for 8-, 16-, and 32-bit modes in little-endian result order. Writes perform byte writes; 32-bit writes occur in descending byte order due to SynQuacer SPI-controller limitations.

## State And Persistence
State is per-device mapped MMIO base plus embedded `tpm_tis_data`. The TPM core owns locality, timeout, and chip registration state.

## Dependencies And Integration Points
Matches OF `socionext,synquacer-tpm-mmio` and ACPI `SCX0009`, uses TIS core PM resume, and does not use interrupts.

## Risks And Edge Cases
Byte order and write order are platform-specific; using generic MMIO helpers could break hardware. IRQ support is absent, so all waits are polling. 16-bit writes return `-EINVAL`, matching core expectations that writes are 8 or 32 bit.

## Test Signals
OF and ACPI probe, byte-wise 32-bit DID/VID reads, descending 32-bit writes, polling-mode TIS commands, and suspend/resume.
