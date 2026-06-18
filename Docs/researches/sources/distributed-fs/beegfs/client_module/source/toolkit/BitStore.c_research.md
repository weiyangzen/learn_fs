## sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.c

**Purpose:** Implements a dynamically sizable bit-vector used by the client for compact flags such as per-stripe first-write tracking.

**Important APIs/types/functions:** Implements `BitStore_setBit`, `setSize`, `clearBits`, `serialize`, `deserializePreprocess`, `deserialize`, `copy`, and `copyThreadSafe`.

**Control flow:** Bits are stored in `lowerBits` for the first machine word and optional `higherBits` for additional blocks. `setBit` bounds-checks then uses atomic kernel bit operations. `setSize` frees/reallocates higher blocks when block count changes and rounds `numBits` to full block capacity. Serialization writes bit count, 8-byte alignment padding, lower/higher blocks, and extra 32-bit padding when needed for cross-arch compatibility. Preprocess validates serialized length and advances the deserialize context.

**State and persistence behavior:** In-memory state is `numBits`, `lowerBits`, and optional `higherBits`. Serialized format is stable across 32/64-bit block size differences by using full 64-bit aligned blocks. `setSize` does not preserve or initialize existing bits; callers usually clear after resizing.

**Dependencies and integration points:** Depends on BeeGFS serialization helpers and `os_kmalloc`. Used by remoting IO handle state to track whether each stripe target has seen its first write.

**Risks:** Thread-safe copy intentionally does not resize and may truncate if destination has fewer blocks. `copy` assumes destination allocation succeeds through no-fail wrappers. `getBit` returns false out of range while `setBit` triggers a bug macro. Serialization/deserialization must stay compatible across word sizes and endianness assumptions in serialization helpers.

**Test signals:** Test set/get/clear across lower and higher blocks, resizing up/down, serialization round-trips on 32-bit and 64-bit builds, malformed deserialize lengths, copy truncation behavior, and concurrent bit set/get paths.
