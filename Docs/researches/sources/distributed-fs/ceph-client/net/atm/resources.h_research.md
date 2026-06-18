# sources/distributed-fs/ceph-client/net/atm/resources.h

## Purpose
`resources.h` declares the ATM device resource manager interface shared by the ATM core, procfs, ioctl, and sysfs code.

## Important APIs and State
- Exposes `atm_devs` and `atm_dev_mutex` for controlled traversal by procfs and related core code.
- Declares `atm_getnames` and `atm_dev_ioctl`, the device enumeration and ioctl dispatch APIs used by `ioctl.c`.
- Under `CONFIG_PROC_FS`, declares seq traversal helpers and per-device proc registration helpers. Without procfs, it provides no-op inline per-device proc hooks.
- Declares `atm_register_sysfs` and `atm_unregister_sysfs`.

## Control Flow and Integration
The header lets `resources.c` own the implementation while `proc.c` uses its seq helpers and `ioctl.c` uses its user-facing operations. The conditional procfs stubs keep device registration logic simple across builds.

## State and Persistence
The header itself owns no state, but it intentionally exposes the global ATM device list and lock. That makes lock ordering and iterator correctness important for all users.

## Dependencies
Depends on `linux/atmdev.h`, `linux/mutex.h`, and conditionally `linux/proc_fs.h`. It is an internal ATM core header.

## Risks and Test Signals
The main risk is misuse of exposed globals without `atm_dev_mutex` or mismatched procfs conditional behavior. Test signals include builds with and without `CONFIG_PROC_FS`, proc device listing while devices register/deregister, and ioctl enumeration using the declared API.
