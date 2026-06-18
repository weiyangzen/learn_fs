# File Research: sources/block-storage/kvdo/vdo/linux/murmurhash3.h

Minimal MurmurHash3 declaration header.

Key responsibilities:
- Provides LGPL/public-domain notice for MurmurHash3.
- Includes Linux integer types.
- Declares `murmurhash3_128(const void *key, int len, uint32_t seed, void *out)`.

Dependencies:
- Requires `<linux/types.h>`.

Notable risks:
- Only the prototype is present; callers must link the implementation elsewhere.
- `len` is `int`, so callers with size_t lengths must ensure values fit.
