# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.h

## Purpose
Vendored Argon2 public header defining parameter limits, error codes, context structure, algorithm types, versions, and API declarations.

## Key Content
Defines min/max bounds for lanes, threads, output, memory, passes, password, salt, secret, and associated data. Declares `argon2_context`, external allocator callback types, `argon2_type`, version constants, flags for clearing password/secret, and all raw/encoded/verify/context APIs.

## Dependencies and Coupling
Included by cryptsetup’s internal Argon2 wrapper and all bundled Argon2 implementation files. Visibility macros adapt for GCC/Clang, MSVC, and default builds.

## Invariants and Risks
Callers must satisfy context pointer/length consistency rules. Different parallelism values intentionally produce different Argon2 outputs. The global `FLAG_clear_internal_memory` is declared here and defined in `core.c`.
