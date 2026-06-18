# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rnd_keys.c

Purpose: supplies deprecated DES random key compatibility wrappers on top of the hcrypto RAND API.

Important APIs/types/functions: `DES_rand_data`, `DES_generate_random_block`, `DES_rand_data_key`, `DES_set_sequence_number`, `DES_set_random_generator_seed`, `DES_new_random_key`, `DES_init_random_number_generator`, and `DES_random_key`.

Control flow: simple wrappers call `RAND_bytes` or `RAND_seed`. `DES_new_random_key` loops until `RAND_bytes` succeeds, fixes odd parity with `DES_set_odd_parity`, and rejects weak DES keys with `DES_is_weak_key`. `DES_random_key` aborts on failure because it has no return code.

State and persistence: no local state is stored. RAND state is affected by seed calls, and generated DES key bytes are written to caller buffers.

Dependencies and integration points: depends on `des.h` and `rand.h`; preserves older DES APIs expected by Kerberos/OpenSSL-compatible code.

Risks and test signals: DES and these APIs are deprecated; `DES_random_key` abort behavior is harsh; RNG failure handling differs between wrappers. Tests should cover parity fixing, weak-key rejection with deterministic RNG hooks, RAND failure propagation, and deprecated symbol availability.
