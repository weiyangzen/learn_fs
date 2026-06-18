# sources/cloud-native/ostree/src/libostree/ostree-kernel-args.h

## Purpose
This public header declares the `OstreeKernelArgs` API for constructing, mutating, parsing, querying, and serializing kernel command-line argument sets used during deployment and bootloader configuration.

## Important APIs and Behavior
The lifecycle surface is `ostree_kernel_args_new()`, `ostree_kernel_args_free()`, and `ostree_kernel_args_cleanup()`. Mutation APIs include `replace_take()`, `replace()`, `replace_argv()`, `append()`, `append_argv()`, `append_argv_filtered()`, `new_replace()`, `delete()`, `delete_key_entry()`, `append_if_missing()`, and `delete_if_present()`. Data import/export APIs include `append_proc_cmdline()`, `parse_append()`, `from_string()`, `to_strv()`, and `to_string()`. Query APIs are `get_last_value()` and `contains()`.

## State, Dependencies, Integration, Risks, and Tests
The type is opaque in the public header, so callers rely on documented ownership transfer and GLib allocation conventions. It depends on `ostree-types.h`, GLib, GObject, and GIO. Integration points include admin deployment commands, bootloader configuration, and tests referenced by the `/proc/cmdline` filter comment. Risks are semantic ambiguity around duplicate keys and whether a key/value argument to `contains()` should imply value matching. Tests should assert API-level behavior without relying on private structures except in dedicated internal tests.
