# sources/distributed-fs/ceph-client/arch/microblaze/lib/lshrdi3.c

Purpose: implements unsigned/logical 64-bit right shift helper `__lshrdi3`.

Important APIs and state: exported `__lshrdi3(long long u, word_type b)` treats both halves as unsigned when shifting.

Control flow: zero shifts return input. Shifts >=32 zero the high word and move shifted old high into low; smaller shifts shift high logically and carry low bits from high.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned 64-bit shifts; endian layout comes from `DWunion`.

Risks and test signals: high word must be zero-filled, not sign-extended. Test values with top bit set and shift counts 0, 31, 32, 63.
