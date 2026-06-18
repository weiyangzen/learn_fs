# sources/compression/xz/src/liblzma/check/crc_common.h

Purpose: shared CRC build-configuration and endian helper header, deciding which CRC32/CRC64 implementations are compiled and declaring the shared lookup tables.

Important APIs/types/functions: declares CRC tables and `lzma_crc32_init()` for small builds; defines byte extraction/shift helpers `A/B/C/D`, `S8/S32/S64`; sets feature macros such as `CRC32_GENERIC`, `CRC64_GENERIC`, `CRC32_ARCH_OPTIMIZED`, `CRC64_ARCH_OPTIMIZED`, `CRC_X86_CLMUL`, `CRC32_ARM64`, and LoongArch-related selection.

Control flow: preprocessor logic chooses implementation availability based on build macros, target architecture, endian mode, Windows constraints, and compiler support. It can select generic table code, x86 CLMUL runtime dispatch, ARM64 CRC32 acceleration, LoongArch CRC acceleration, or a combination.

State and persistence: no runtime state, but it controls whether global tables and dispatch function pointers exist in the compiled objects.

Dependencies/integration: includes `common.h`, architecture-specific headers through downstream files, and build-system feature probes. `crc32_fast.c`, `crc64_fast.c`, small CRC files, and LZ hash code rely on its declarations.

Risks: this is configuration-critical. A wrong macro combination can compile no valid implementation, duplicate definitions, or use instructions unavailable on the runtime CPU. Endian helper mistakes affect all fast CRC math. Windows and E2K special cases need careful preservation.

Test signals: matrix builds across small/fast, endian, x86 CLMUL, ARM64, LoongArch, Windows, and no-constructor configurations. Known CRC vectors should pass for every selected implementation.
