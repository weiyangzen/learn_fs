# `sources/distributed-fs/ceph-client/include/linux/usb/gadget_configfs.h`

## Purpose

`gadget_configfs.h` provides macro helpers for configfs-backed USB gadget string attributes and per-language string groups. It is a small metaprogramming header used by gadget configfs implementations to avoid repeating show/store and group creation boilerplate.

## Important APIs, Types, and Constants

- `GS_STRINGS_W()` emits a configfs store method that resolves the owning structure with `to_<struct>()` and updates a string field through `usb_string_copy()`.
- `GS_STRINGS_R()` emits a show method returning the string field or an empty string.
- `GS_STRINGS_RW()` combines read/write generation with `CONFIGFS_ATTR()`.
- `USB_CONFIG_STRING_RW_OPS()` emits config item operations and item type objects for language-specific string entries.
- `USB_CONFIG_STRINGS_LANG()` emits `make_group`, `drop_item`, group operations, and type objects for creating language-specific string groups while enforcing duplicate-language and `MAX_USB_STRING_LANGS` limits.

## Control Flow and Lifetimes

When userspace creates a configfs string language directory, generated `*_strings_make()` allocates a language structure, validates the directory name through `check_user_usb_string()`, initializes the config group, checks for duplicate language IDs in the parent string list, enforces the maximum language count, and links the new object. Dropping the configfs item releases it through normal configfs reference handling.

## State and Persistence Behavior

The macros maintain in-kernel configfs object state only. The generated code stores language objects in the parent object's `string_list` and stores mutable string values in fields selected by the macro caller. Persistence is configfs lifetime persistence: objects exist while userspace keeps the configfs entries and references alive.

## Dependencies and Integration Points

The header depends on `linux/configfs.h`, USB gadget string helpers, `usb_string_copy()`, `check_user_usb_string()`, `MAX_USB_STRING_LANGS`, config item release callbacks, and caller-provided object layouts with `group`, `list`, `stringtab_dev`, `strings_group`, and `string_list` members.

## Risks and Edge Cases

Because it generates C identifiers and assumes structure names, misusing the macros fails at compile time or creates wrong object ownership. The language creation path must free allocation on every validation failure. String store semantics depend on `usb_string_copy()` sanitizing and allocating correctly. Duplicate-language checks are list-based and require external list locking/serialization from configfs operations.

## Test Signals

Build gadget configfs users, create/remove multiple language directories, test duplicate language IDs, exceed `MAX_USB_STRING_LANGS`, write/read generated string attributes, verify cleanup under allocation or validation failure, and run configfs reference-count diagnostics during gadget removal.
