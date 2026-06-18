# sources/distributed-fs/orangefs/src/common/hash/murmur3.c

Purpose: Public-domain MurmurHash3 reference implementation providing 32-bit and 128-bit non-cryptographic hashes.

Important APIs/functions: `MurmurHash3_x86_32()`, `MurmurHash3_x86_128()`, and `MurmurHash3_x64_128()` implement platform-tuned variants. Helpers include rotate functions/macros, `getblock()`, `fmix32()`, and `fmix64()`.

Control flow: Each hash function initializes seed-derived hash state, processes fixed-size body blocks, folds in tail bytes with fall-through `switch` logic, xors length, applies avalanche finalization, and writes the result to caller-provided output storage.

State/persistence: Stateless and deterministic. No memory allocation or persistent state.

Dependencies/integration: Includes `murmur3.h` for fixed-width integer types and prototypes. Used wherever OrangeFS needs stable non-cryptographic hashing.

Risks: `getblock(p, i) (p[i])` assumes native endian and tolerates whatever alignment the platform allows; strict-alignment or cross-endian portability may need adjustment. The x86 and x64 128-bit variants intentionally produce different results. Fall-through switch cases rely on compiler acceptance without annotations.

Test signals: Compare known MurmurHash3 vectors for each variant, test empty input, unaligned input buffers, tail lengths 1-15, and deterministic seed behavior.
