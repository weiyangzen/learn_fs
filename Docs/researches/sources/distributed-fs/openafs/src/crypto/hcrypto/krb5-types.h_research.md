# sources/distributed-fs/openafs/src/crypto/hcrypto/krb5-types.h

This Windows-specific compatibility header supplies C99-style integer typedefs when building under `AFS_NT40_ENV`. It maps `int8_t`, `int16_t`, `int32_t`, `int64_t`, unsigned variants, and BSD-style `u_int*_t` aliases to Microsoft `__int*` types.

There is no runtime control flow or persistence. Dependencies are `AFS_NT40_ENV` and MSVC type support. Integration is hcrypto/Heimdal code that expects fixed-width types before full stdint availability. Risks are duplicate typedefs if modern Windows builds include `stdint.h` first, and differences in signedness/width assumptions. Test signals are Windows hcrypto compile coverage and ABI checks for fixed-width crypto structs.
