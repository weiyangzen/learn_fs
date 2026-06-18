<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h

## Purpose
`sysfs.h` is bcache's macro layer for kobject sysfs implementation. It standardizes kobj types, show/store declarations, locked wrappers, attribute declarations, formatting helpers, and parsers.

## Important APIs, Types, And Functions
`KTYPE(type)` constructs a `const struct kobj_type`. `SHOW()`, `STORE()`, `SHOW_LOCKED()`, and `STORE_LOCKED()` generate callbacks. `write_attribute()`, `read_attribute()`, and `rw_attribute()` declare attributes. Formatting helpers include `sysfs_printf()`, `sysfs_print()`, `sysfs_hprint()`, and `var_*`; parsing helpers include `sysfs_strtoul()`, `sysfs_strtoul_bool()`, `sysfs_strtoul_clamp()`, `strtoul_or_return()`, `strtoi_h_or_return()`, and `sysfs_hatoi()`.

## Control Flow
Show/store functions in `sysfs.c` use macro checks that compare the active `attr` with a generated `sysfs_*` object. On match, the helper emits output, parses input, updates a variable, or returns an error. Locked wrappers serialize a generated body with `bch_register_lock`.

## State And Persistence
The header owns no state. It mutates caller-provided variables only; persistence is controlled by the caller through explicit superblock or UUID writes.

## Dependencies, Integration Points, Risks, And Test Signals
It assumes `bch_register_lock`, `bch_hprint()`, `strtoi_h()`, and kernel sysfs types are visible. Risks are hidden returns, format-type fallback in `sysfs_print()`, global serialization, and misuse of direct-return parsing macros. Test by compiling every generated kobject type and exercising bool, bounded integer, human-size, string-list, unknown-attribute, and concurrent locked sysfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h -->
