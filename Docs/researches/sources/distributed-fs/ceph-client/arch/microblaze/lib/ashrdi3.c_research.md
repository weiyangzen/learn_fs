# sources/distributed-fs/ceph-client/arch/microblaze/lib/ashrdi3.c

Purpose: implements signed 64-bit arithmetic right shift helper `__ashrdi3`.

Important APIs and state: exported `__ashrdi3(long long u, word_type b)` uses the high word sign bit for sign extension.

Control flow: zero shifts return input. Shifts >=32 fill high with sign bits and shift the old high word into low; smaller shifts shift high arithmetically and carry low bits from high.

State and persistence: pure arithmetic.

Dependencies and integration: used for compiler-generated signed 64-bit shifts in core and modules; depends on endian-aware `DWunion`.

Risks and test signals: sign-extension correctness is critical around negative values. Test positive/negative values and boundaries 0, 31, 32, 63.
