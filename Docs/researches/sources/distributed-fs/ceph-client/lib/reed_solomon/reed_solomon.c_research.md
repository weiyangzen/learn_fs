## sources/distributed-fs/ceph-client/lib/reed_solomon/reed_solomon.c

Purpose: runtime-configurable Reed-Solomon encoder/decoder library. It manages shared codec tables and per-user control structures, then exposes width-specific encode/decode wrappers depending on config.

Important APIs/types: `struct rs_codec` holds GF parameters, lookup tables, generator polynomial, and user count. `struct rs_control` points to a codec and contains decode scratch buffers. Public APIs include `init_rs_gfp()`, `init_rs_non_canonical()`, `free_rs()`, and conditional `encode_rs8/16()` and `decode_rs8/16()`.

Control flow: `codec_init()` allocates tables, builds `alpha_to`/`index_of`, verifies the primitive polynomial/function, computes `iprim`, and builds generator polynomial in index form. `init_rs_internal()` validates parameters, allocates the control plus decode buffers, reuses a matching codec from `codec_list` under `rslistlock`, or creates a new one. `free_rs()` decrements codec users and frees tables when the last control releases it.

State and persistence: global `codec_list` persists shared codecs under mutex protection. Each control owns decode buffers, so decode calls on a single control must be serialized.

Dependencies/integration: depends on `linux/rslib.h`, slab allocation, mutexes, and included generic encoder/decoder bodies. Intended for drivers/subsystems needing configurable RS codes.

Risks/test signals: parameter validation prevents impossible fields, but primitive polynomial correctness is only detected during table generation. Allocation can be expensive and should happen at init time. `test_rslib.c` provides randomized validation over many symbol sizes and padding levels.
