# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-sysfs.c

## Purpose

`fbtft-sysfs.c` exposes runtime controls for FBTFT devices. It parses and displays gamma curves and exposes a writable debug bitmask attribute on the framebuffer device.

## Important APIs, Types, and Functions

Exported functions are `fbtft_gamma_parse_str()`, `fbtft_expand_debug_value()`, `fbtft_sysfs_init()`, and `fbtft_sysfs_exit()`. Attribute handlers are `show_gamma_curve()`, `store_gamma_curve()`, `show_debug()`, and `store_debug()`. The parser uses `get_next_ulong()` over newline/space-separated hex values after normalizing commas and semicolons.

## Control Flow

Registration calls `fbtft_sysfs_init()`, resolves the fb device via `dev_of_fbinfo()`, creates `debug`, and conditionally creates `gamma` when curves and a setter exist. A gamma write is copied, normalized, parsed into a fixed temporary array, applied to hardware through `set_gamma()`, and then copied into `par->gamma.curves` under `gamma.lock`. Debug writes parse decimal input and expand shorthand levels 1 through 7 into bitmasks.

## State and Persistence Behavior

The sysfs state is volatile. `par->debug` changes immediately for future debug checks. `par->gamma.curves` is the kernel cache of the last successfully applied gamma table; hardware persistence depends on the panel controller and is lost on reset/power loss.

## Dependencies and Integration Points

The file integrates with fbdev device lookup, sysfs device attributes, FBTFT operation callbacks, and the gamma storage initialized by `fbtft_framebuffer_alloc()`.

## Risks and Edge Cases

`sprintf_gamma()` calls `scnprintf(&buf[len], PAGE_SIZE, ...)` without subtracting the current offset, so the remaining buffer bound is overstated. The parser accepts exactly the configured curve/value counts and rejects too many or too few values, but malformed whitespace or empty fields propagate `kstrtoul()` errors. `device_create_file()` return values are ignored, so missing attributes are only visible indirectly. `debug` uses mode `0660`, requiring correct device ownership for non-root access.

## Test Signals

Test gamma strings with commas, semicolons, newlines, too few/many curves, invalid hex, maximum 128 values, and hardware `set_gamma()` failure. Verify sysfs creation/removal, debug shorthand expansion, concurrent gamma read/write locking, and PAGE_SIZE formatting behavior.
