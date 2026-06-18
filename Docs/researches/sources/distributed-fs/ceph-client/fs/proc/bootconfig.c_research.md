# sources/distributed-fs/ceph-client/fs/proc/bootconfig.c

Purpose: Exposes parsed boot configuration through `/proc/bootconfig` when boot config support is built.

Important APIs and types: Uses `saved_boot_config`, bootconfig iterators such as `xbc_for_each_key_value()`, `xbc_node_compose_key()`, `xbc_node_get_child()`, `xbc_array_for_each_value()`, `xbc_node_is_array()`, `cmdline_has_extra_options()`, and `boot_command_line`. Registers a proc single file with `proc_create_single()`.

Control flow: At `fs_initcall`, `proc_boot_config_init()` computes the required output length by calling `copy_xbc_key_value_list(NULL, 0)`, allocates a buffer, fills it with formatted `key = "value"` lines and optional bootloader parameter comments, then creates `/proc/bootconfig`. Reads simply dump the saved buffer through `boot_config_proc_show()`.

State and persistence: The formatted boot config is copied once into `saved_boot_config` during init and persists for the lifetime of the kernel. It is a read-only snapshot of early boot configuration rather than live state.

Dependencies and integration points: Depends on `CONFIG_BOOT_CONFIG` object selection, the bootconfig parser, procfs single-file helpers, slab allocation, and global boot command-line data.

Risks: The two-pass length computation depends on `snprintf()` accounting and stable bootconfig data between passes. Quote selection must preserve values containing double quotes. Allocation failure prevents the file from containing data but returns an init error only for allocation/format failures; proc creation is not checked for failure.

Test signals: Boot with no bootconfig, scalar values, arrays, values containing quotes, extra bootloader options, and long key/value lists; verify `/proc/bootconfig` formatting and absence/presence with `CONFIG_BOOT_CONFIG`.
