# sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.h

## Purpose

`platform-access.h` defines the private state for PSP platform-access support and declares its init/destroy functions.

## Important APIs, Types, And Functions

`struct psp_platform_access_device` stores device and PSP pointers, `platform_access_vdata`, separate mailbox and doorbell mutexes, and an opaque data pointer. It declares `platform_access_dev_init()` and `platform_access_dev_destroy()`.

## Control Flow

The header itself has no control flow. It provides the shared layout used by platform-access setup, teardown, and message-sending code.

## State And Persistence Behavior

Instances persist as `psp->platform_access_data`. The mutexes protect serialized access to PSP hardware command registers.

## Dependencies And Integration Points

It includes platform-access UAPI/private request definitions and `psp-dev.h`, binding this state to PSP subdevice initialization.

## Risks And Test Signals

Risks are field-layout drift and missing cleanup of initialized mutexes. Build coverage plus probe/remove tests on PSP devices with platform-access vdata validate the header contract.
