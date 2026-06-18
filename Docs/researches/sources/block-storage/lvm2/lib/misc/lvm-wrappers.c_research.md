# File Research: sources/block-storage/lvm2/lib/misc/lvm-wrappers.c

This file provides wrappers around udev, page size, entropy, and unbiased random selection.

Main APIs:
- `udev_init_library_context()`, `udev_fin_library_context()`, `udev_is_running()`, `udev_get_library_context()`.
- `lvm_getpagesize()`.
- `read_urandom()`.
- `lvm_even_rand()`.

Behavior:
- With `UDEV_SYNC_SUPPORT`, creates a `udev` context unless `DM_DISABLE_UDEV` is set, checks active udev queue, and exposes the context.
- Without `UDEV_SYNC_SUPPORT`, udev functions become safe stubs.
- `read_urandom()` opens `/dev/urandom`, verifies it is a character device, reads exactly requested bytes, and closes.
- `lvm_even_rand()` rejects modulo-biased values from the incomplete top slice of `RAND_MAX`.

Risks:
- `read_urandom()` performs a single `read()` and treats short reads as failure.
- `lvm_even_rand()` uses `rand_r`, suitable for utility randomness, not cryptographic use.
