# sources/distributed-fs/beegfs/common/tests/TestUint128.cpp

Purpose: This suite validates BeeGFS `uint128_t` helpers for construction, formatting, byte-order conversion, hashing, ordering, and streaming.

Important APIs/types/functions: It uses `uint128::make`, `upper64`, `lower64`, `toHexStr`, `uint128::Hash`, `HOST_TO_LE_128`, `HOST_TO_BE_128`, `LE_TO_HOST_128`, and `operator<<`. The fixture table covers zero, all-ones, high-only, low-only, and a mixed-value case with expected normal and reversed byte order strings.

Control flow: Tests loop over the fixture table to verify high/low extraction, hex formatting, endian conversions conditional on host byte order, insertion/lookup in `std::unordered_map` and `std::map`, and stream concatenation output.

State and persistence behavior: All state is local in maps and values. The behavior matters for serialized IDs, checksums, and map keys that may persist or cross process boundaries.

Dependencies and integration: It includes `StringTk` and serialization byteswap helpers. Correct 128-bit hashing and ordering are necessary when these values are used as keys in containers.

Risks and test signals: Coverage is solid for powers of two and representative constants. It does not cover parsing from strings, arithmetic beyond repeated doubling, overflow behavior, or ABI representation on compilers without native 128-bit support.
