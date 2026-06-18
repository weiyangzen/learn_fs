# sources/distributed-fs/ceph-client/arch/microblaze/lib/ashldi3.c

Purpose: implements the libgcc ABI helper `__ashldi3` for 64-bit arithmetic left shifts on 32-bit MicroBlaze.

Important APIs and state: `__ashldi3(long long u, word_type b)` uses `DWunion` from `libgcc.h` and is exported to modules.

Control flow: zero shifts return unchanged. Shifts >=32 move the low word into the high word and clear low; smaller shifts combine shifted high word with carry bits from low.

State and persistence: pure arithmetic, no persistent state.

Dependencies and integration: compiler-generated 64-bit shifts and modules may call it; endian layout comes from `libgcc.h`.

Risks and test signals: shift counts outside compiler-expected ranges are not specially masked. Test 0, 1, 31, 32, 63-bit shifts on both endian configurations.
