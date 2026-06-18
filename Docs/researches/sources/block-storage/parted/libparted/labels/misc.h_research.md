# File Research: sources/block-storage/parted/libparted/labels/misc.h

This header provides small shared inline helpers for libparted label implementations.

Key APIs:
- `generate_random_uint32()`: uses `uuid_generate()` to obtain random bytes, returns the first `uint32_t`, and substitutes `0xffffffff` if the generated value is zero.
- `is_linux_swap(char const *fs_type_name)`: returns true when a filesystem type name starts with `linux-swap`.

Integration:
- `dos.c` uses `generate_random_uint32()` for nonzero MBR disk signatures and `is_linux_swap()` for type-ID selection.
- `mac.c` uses `is_linux_swap()` when mapping filesystem types to Apple partition semantics.
- Requires `<uuid/uuid.h>` and `<inttypes.h>`; assumes callers include string declarations as needed through surrounding includes.

Risk notes:
- `generate_random_uint32()` intentionally uses only four bytes of a UUID, so uniqueness is limited to 32 bits.
- The helper avoids zero because zero can be interpreted as no FAT serial number or no MBR signature.
