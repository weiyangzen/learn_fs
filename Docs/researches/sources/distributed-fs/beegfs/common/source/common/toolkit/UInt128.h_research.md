<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h

**Purpose:** Defines BeeGFS's unsigned 128-bit integer alias plus helpers for construction, splitting, hashing, hex formatting, and stream output.

**Important APIs/types/functions:** `typedef unsigned __int128 uint128_t`, `Uint128Vector`, `uint128::Hash`, `make`, `lower64`, `upper64`, `toHexStr`, and global `operator<<`.

**Control flow:** `make` shifts the most significant word into the upper 64 bits and ORs the lower word. Formatting emits two zero-padded 16-hex-digit halves. Hashing XORs upper and lower halves to avoid standard library implementations that ignore the high half.

**State and persistence behavior:** Stateless value helpers. Hex string output is deterministic and suitable for logs or textual persistence.

**Dependencies and integration points:** Used by serialization byte swapping and any common code needing 128-bit IDs or hashes. Depends on GCC/Clang `unsigned __int128`.

**Risks:** Non-standard integer type may limit portability. XOR hash is simple and can collide for values with swapped/equal halves. Stream operator is global for `uint128_t`.

**Test signals:** Tests should verify make/split round trips, hex padding, hash high-half sensitivity, and byte-swap interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UInt128.h -->
