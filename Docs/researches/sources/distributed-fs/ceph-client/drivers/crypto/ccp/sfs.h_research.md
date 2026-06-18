# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.h

## Purpose

`sfs.h` defines the private structures for PSP Seamless Firmware Servicing support.

## Important APIs, Types, And Functions

It defines `struct sfs_misc_dev`, packed `struct sfs_command`, and `struct sfs_device`. The command layout embeds `struct psp_ext_req_buffer_hdr`, a one-page status/extended buffer, and a flexible SFS payload buffer. It declares `sfs_dev_init()` and `sfs_dev_destroy()`.

## Control Flow

The header contains no executable flow. Its layout is consumed by `sfs.c` to cast the 2 MiB command buffer into an extended mailbox request plus payload area.

## State And Persistence Behavior

`struct sfs_device` persists as `psp->sfs_data` and owns the HV-fixed page and misc-device reference.

## Dependencies And Integration Points

It includes SFS UAPI, PSP SEV/platform-access definitions, memory attribute helpers, and `psp-dev.h`.

## Risks And Test Signals

Risks include packed flexible-array layout drift and mismatch with PSP extended command expectations. Build tests and live SFS firmware-version queries validate it.
