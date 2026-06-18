# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.h

## Purpose
`sysfs.h` declares firmware class sysfs interfaces, fallback configuration accessors, `struct fw_sysfs`, and upload integration hooks.

## Important APIs, Types, And Functions
It imports the `FIRMWARE_LOADER_PRIVATE` namespace, declares `fw_fallback_config`, `dev_attr_loading`, registration helpers, `struct fw_sysfs`, `to_fw_sysfs()`, `__fw_load_abort()`, `fw_load_abort()`, `fw_create_instance()`, and upload attribute/hooks when `CONFIG_FW_UPLOAD` is enabled.

## Control Flow, State, And Persistence
When user-helper is enabled, inline accessors read and write the global fallback timeout. When sysfs support is disabled, registration functions stub out to success. `fw_sysfs` stores the class device, firmware object, private firmware state, async flag, and optional upload private data.

## Dependencies, Integration Points, Risks, And Test Signals
The header connects fallback, sysfs, upload, and core firmware state. Risks are configuration-dependent stubs hiding missing sysfs behavior, namespace import requirements, and callers assuming upload hooks exist when compiled out. Test signals include build coverage for sysfs off, user-helper off, upload off, timeout helper use, and aborting through a `fw_sysfs` wrapper.
