# sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.h

Purpose: public CRC32C API declarations for zfile and tests.

Important APIs/types/functions: namespace `crc32` declares `crc32c(const void*, size_t)`, `crc32c(const std::string&)`, `crc32c_extend(const void*, size_t, uint32_t)`, and `crc32c_extend(const std::string&, uint32_t)`. Nested `crc32::testing` declares `crc32c_slow` and `crc32c_fast`.

Control flow: no runtime logic in the header. Consumers call the functions implemented in `crc32c.cpp`.

State and persistence: no header state. Returned CRC values are used by zfile integrity checks and can become persistent checksums in file formats.

Dependencies/integration: depends on `stdint.h` and `std::string`. Included by `crc32c.cpp` and zfile code needing checksums.

Risks: the testing fast function is exposed in the public header and can be misused on unsupported hardware if called directly. ABI depends on namespace and overload signatures remaining stable for linked consumers.

Test signals: the testing declarations allow direct slow/fast comparison in unit tests.
