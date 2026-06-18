# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.h

## Purpose

`sev-dev-tio.h` defines shared SEV-TIO data structures used by the PSP TIO firmware interface and the PCI TSM/IDE integration layer.

## Important APIs, Types, And Functions

Important types are packed `struct sla_addr_t`, `struct tsm_spdm`, `struct tsm_dsm_tio`, `struct tio_dsm`, `struct spdm_dobj_hdr`, and `struct sev_tio_status`. It declares TIO lifecycle functions and constants such as `SEV_TIO_MAX_COMMAND_LENGTH`, `TIO_IDE_MAX_TC`, and SPDM data object IDs.

## Control Flow

The header has no executable flow. Its structures allow `sev-dev-tio.c` to store firmware/SLA command state and `sev-dev-tsm.c` to drive PCI TSM connect/disconnect operations.

## State And Persistence Behavior

`struct tsm_dsm_tio` is the persistent per-PCI-device TIO state: firmware context, SPDM buffers, current command continuation data, and IDE stream handles. `struct sev_tio_status` caches firmware-advertised buffer limits and capabilities.

## Dependencies And Integration Points

It includes PCI TSM, PCI IDE, generic TSM, and SEV UAPI headers. It also forward-couples to `struct sev_device` through `struct tio_dsm`.

## Risks And Test Signals

Risks include packed bitfield and firmware ABI layout drift, undersized command replay buffer, and SPDM object length mismatches. Compile-time layout checks in implementation plus TIO firmware status validation and PCI TSM connect tests are key signals.
