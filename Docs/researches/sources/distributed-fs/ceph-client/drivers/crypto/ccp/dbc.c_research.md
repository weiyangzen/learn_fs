# sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.c

## Purpose

`dbc.c` implements the AMD Secure Processor Dynamic Boost Control misc-device interface. It lets privileged userspace authenticate and exchange DBC nonce, UID, and parameter messages with PSP firmware, using either platform-access mailbox commands or the PSP extended mailbox path depending on advertised capability.

## Important APIs, Types, And Functions

The external lifecycle functions are `dbc_dev_init()` and `dbc_dev_destroy()`. The user entry point is `dbc_ioctl()` on `/dev/dbc`. `send_dbc_cmd()` abstracts transport selection and maps PSP firmware status codes to Linux errors through `error_codes`. `send_dbc_nonce()` retries once on `-EAGAIN`, and `send_dbc_parameter()` chooses get/set firmware commands based on `dbc_user_param.msg_index`.

## Control Flow

Probe allocates one page for `union dbc_buffer`, initializes transport-specific header, result, payload, and payload-size pointers, probes availability with a nonce command, then registers a mode `0600` misc device. Each ioctl obtains the master PSP, serializes with `ioctl_mutex`, copies the fixed-size user structure into the shared payload area, sets payload size, sends the relevant firmware message, and copies the payload back to userspace.

## State And Persistence Behavior

Persistent state is `struct psp_dbc_device` stored in `psp->dbc_data`, including the command page and transport-selection fields. Firmware authentication state may survive driver initialization; `-EACCES` from the initial nonce is treated as already authenticated. The command buffer is reused across ioctls under a mutex.

## Dependencies And Integration Points

DBC depends on PSP master selection, `psp_extended_mailbox_cmd()`, `psp_send_platform_access_msg()`, `uapi/linux/psp-dbc.h`, and platform feature probing in `psp-dev.c`. It must initialize after platform access because non-extended transport uses the platform-access mailbox.

## Risks And Test Signals

Risks include stale shared-buffer contents, incorrect firmware-status translation, transport mismatch when capability bits are wrong, and fixed-size user-copy assumptions diverging from UAPI structures. Test by checking `/dev/dbc` permissions, exercising nonce/UID/get/set parameter ioctls on both transports, forcing PSP status errors, and verifying concurrent ioctl serialization.
