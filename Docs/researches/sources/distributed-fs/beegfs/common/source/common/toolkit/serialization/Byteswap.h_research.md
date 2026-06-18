<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h

**Purpose:** Supplies byte-swap functions and host/little-endian/big-endian conversion macros for 16-, 32-, 64-, and 128-bit values.

**Important APIs/types/functions:** `byteswap16`, `byteswap32`, `byteswap64`, `byteswap128`, and macros `HOST_TO_LE_*`, `HOST_TO_BE_*`, `LE_TO_HOST_*`, and `BE_TO_HOST_*`.

**Control flow:** Wider swaps compose smaller swaps. `byteswap128` swaps the lower and upper 64-bit halves and uses `uint128::make`. Macro definitions depend on compile-time `BYTE_ORDER`.

**State and persistence behavior:** Stateless transformations. They define the wire/on-disk little-endian representation used by `Serialization.h`.

**Dependencies and integration points:** Depends on `UInt128.h` and system endian macros. Serializer/deserializer primitive conversions use these macros.

**Risks:** The `BE_TO_HOST_*` macros are defined through `HOST_TO_LE_*`, which is correct for little-endian hosts but suspicious for big-endian hosts where big-endian-to-host should be identity; this should be reviewed before using BE macros. Macro-based conversions can double-evaluate expressions if expanded with side effects.

**Test signals:** Unit tests should verify all swap widths and all conversion macros under little- and big-endian configurations, especially `BE_TO_HOST_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Byteswap.h -->
