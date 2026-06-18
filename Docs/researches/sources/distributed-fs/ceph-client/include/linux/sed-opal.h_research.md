# sources/distributed-fs/ceph-client/include/linux/sed-opal.h

Purpose: `sed-opal.h` is the block-layer interface for TCG Opal Self-Encrypting Drive support. It exposes device initialization, suspend unlock, ioctl dispatch, and a helper for recognizing Opal ioctls.

Important APIs/types/functions: `struct opal_dev` is opaque. `sec_send_recv` abstracts SECURITY SEND/RECEIVE transport. With `CONFIG_BLK_SED_OPAL`, exported APIs are `init_opal_dev()`, `free_opal_dev()`, `opal_unlock_from_suspend()`, `sed_ioctl()`, and `is_sed_ioctl()`. The header defines boot key names `OPAL_AUTH_KEY` and `OPAL_AUTH_KEY_PREV`. Disabled builds return NULL/false/no-op or zero for ioctl dispatch.

Control flow: A block driver creates an Opal device with its transport callback, forwards recognized ioctls to `sed_ioctl()`, and frees the Opal context at teardown. Resume paths may call `opal_unlock_from_suspend()` to restore access.

State and persistence behavior: `struct opal_dev` owns runtime discovery and session state. Commands mutate persistent drive locking ranges, credentials, shadow MBR state, and ownership on the device. The key-name constants integrate with persistent boot PIN storage.

Dependencies and integration points: It depends on UAPI `sed-opal.h`, block device ioctl paths, SCSI/NVMe/security command transports, suspend/resume, and optional SED key storage.

Risks: Disabled `sed_ioctl()` returning zero can hide accidental dispatch unless callers gate with `is_sed_ioctl()`. Opal operations are security-sensitive and often destructive (`REVERT`, secure erase, password changes). Transport callbacks must preserve buffer lengths and command direction.

Test signals: All listed `IOC_OPAL_*` recognition, enabled/disabled config behavior, discovery, ownership, lock/unlock, LR setup/status, suspend unlock, password rotation, shadow MBR writes, generic table access, and error injection from the transport callback.
