# File Research: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.h

`sysfs.h` is a macro utility header for bcache sysfs files. It defines `KTYPE()` to build `struct kobj_type` instances with local show/store functions and default attribute arrays. `SHOW()`, `STORE()`, `SHOW_LOCKED()`, and `STORE_LOCKED()` standardize sysfs handler definitions, with locked variants wrapping calls in `bch_register_lock`.

Attribute declaration helpers create write-only, read-only, and read-write `struct attribute`s. Print helpers select formatting based on C type, append newlines, or use `bch_hprint()` for human-readable byte values. `var_print`/`var_printf`/`var_hprint` pair those helpers with a local `var()` macro pattern used heavily in `sysfs.c`.

Store helpers parse decimal integers, booleans, clamped unsigned longs, and human-readable sizes. The `strtoul_or_return()` and `strtoi_h_or_return()` macros deliberately return parse errors directly from the surrounding sysfs store function. This header therefore assumes use inside sysfs show/store functions with `attr`, `buf`, and `size` variables in scope.
