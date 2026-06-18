# File Research: sources/block-storage/lvm2/libdm/libdm-common.h

## Purpose

`libdm-common.h` is the internal shared header for libdevmapper common helpers. It exposes macros and helper declarations used across the libdm implementation, especially by ioctl/task code and dependency-tree code.

## Contents

- Includes public libdevmapper API definitions through `libdm/libdevmapper.h`.
- Defines `DM_DEFAULT_NAME_MANGLING_MODE_ENV_VAR_NAME`.
- Defines convenience macros:
  - `DEV_NAME(dmt)` returns `mangled_dev_name` when present, otherwise `dev_name`.
  - `DEV_UUID(dmt)` returns `mangled_uuid` when present, otherwise `uuid`.

## Declared Functions

- String mangling:
  - `mangle_string()`
  - `unmangle_string()`
  - `check_multiple_mangled_string_allowed()`
- Target construction:
  - `create_target()`
- Device-node queueing and direct-support APIs:
  - `add_dev_node()`
  - `rm_dev_node()`
  - `rename_dev_node()`
  - `get_dev_node_read_ahead()`
  - `set_dev_node_read_ahead()`
  - `update_devs()`
- SELinux cleanup:
  - `selinux_release()`
- Suspend counter helpers:
  - `inc_suspended()`
  - `dec_suspended()`
- Thin-pool and kernel-version helpers implemented outside this file group:
  - `parse_thin_pool_status()`
  - `get_uname_version()`

## Dependencies and Role

This header forms an internal contract between `libdm-common.c`, `libdm-deptree.c`, and other libdm source files. It is not just a public API declaration file; it exposes internal mechanics such as mangled task fields and queued device-node operations.

## Notable Details

`DEV_NAME()` and `DEV_UUID()` centralize the rule that ioctl calls should use the mangled value when one was generated. That keeps public callers working with their original strings while kernel/udev-facing paths receive the escaped variant when necessary.
