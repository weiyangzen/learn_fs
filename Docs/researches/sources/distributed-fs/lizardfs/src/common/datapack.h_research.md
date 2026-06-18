# sources/distributed-fs/lizardfs/src/common/datapack.h

Purpose: provides inline big-endian serialization/deserialization helpers for fixed-width integers in MooseFS/LizardFS protocol buffers.

Important APIs/types/functions: `put64bit`, `put32bit`, `put16bit`, `put8bit`, `get64bit`, `get32bit`, `get16bit`, and `get8bit`.

Control flow: each `put` writes bytes in network/big-endian order and advances a mutable `uint8_t**`. Each `get` reconstructs the integer from a `const uint8_t**` and advances the read pointer.

State and persistence: no internal state; it mutates caller-provided buffer pointers and buffer contents.

Dependencies and integration: depends only on `platform.h` and integer types. Used in low-level wire/disk record packing where avoiding stream abstractions matters.

Risks: no bounds checks, alignment checks, or null checks; callers must guarantee sufficient buffer. The pointer-to-pointer API is efficient but easy to misuse.

Test signals: no direct tests in this subset; protocol round-trip tests elsewhere likely cover it indirectly.
