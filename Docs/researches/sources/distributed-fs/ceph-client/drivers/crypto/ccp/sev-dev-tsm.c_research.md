# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tsm.c

## Purpose

`sev-dev-tsm.c` connects SEV-TIO firmware operations to the Linux PCI TSM framework. It probes eligible PF0 PCI devices, establishes SPDM sessions over DOE, configures PCI IDE streams, and tears those streams down during disconnect.

## Important APIs, Types, And Functions

The external functions are `sev_tsm_init_locked()` and `sev_tsm_uninit()`. `sev_tsm_ops` provides `.probe`, `.remove`, `.connect`, and `.disconnect` callbacks. Helpers include `sev_tio_spdm_cmd()`, IDE stream setup/enable/register/teardown functions, `tio_pf0_probe()`, `dsm_create()`, `dsm_connect()`, and `dsm_disconnect()`.

## Control Flow

Initialization calls `sev_tio_init_locked()`, registers a TSM device, copies TIO status, and stores `sev->tsmdev`/`sev->tio_status`. TSM probe constructs a PF0 object for devices that qualify. Connect verifies the DOE mailbox supports secure session, allocates an IDE stream for traffic class 0, creates the firmware TIO device context, programs IDE stream identifiers and default stream settings, runs `TIO_DEV_CONNECT`, loops through SPDM DOE exchanges until firmware succeeds, enables/registers IDE streams, and unwinds on errors. Disconnect attempts normal then forced firmware disconnect, reclaims TIO context, disables/unregisters streams, and frees IDE state.

## State And Persistence Behavior

The `struct tio_dsm` allocated at probe owns the per-device TIO state. Stream state is mirrored in PCI IDE structures and in firmware device context buffers. The SEV device stores the registered `tsm_dev` and a cached copy of TIO status until uninit.

## Dependencies And Integration Points

It depends on the Linux PCI TSM framework, PCI DOE, PCI IDE namespace, PSP/SEV TIO helpers, IOMMU/SEV platform initialization, and PCI root-port topology helpers. It is invoked from SNP initialization when firmware and IOMMU both support SEV-TIO.

## Risks And Test Signals

Risks include incomplete unwind ordering around IDE stream enable/register, assumptions that traffic class 0 is always present, DOE mailbox mismatch, forced root-port CFG/TEE settings, and disconnect during shutdown/restart. Test with TSM-capable PF0 devices, DOE CMA and secure-session traffic, IDE stream enable/register failure injection, connect/disconnect cycles, and system shutdown forced disconnect paths.
