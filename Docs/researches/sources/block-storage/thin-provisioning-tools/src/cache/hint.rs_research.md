# File Research: sources/block-storage/thin-provisioning-tools/src/cache/hint.rs

Defines the on-disk cache policy hint value type. It is a fixed 4-byte payload.

Key behavior:
- `Hint { hint: [u8; 4] }` is `Clone`, `Copy`, and `Default`.
- Implements `Unpack` with `disk_size() == 4`, copying the first four bytes from input.
- Implements `Pack` by writing each byte back in order.

This type is used by cache dump, restore, check, and metadata generation for policy hint arrays.
