## sources/distributed-fs/ceph-client/lib/reed_solomon/test_rslib.c

Purpose: kernel module self-test for the generic Reed-Solomon library across multiple field sizes, generator polynomials, roots, padding amounts, correction modes, and beyond-capacity cases.

Important APIs/types: module parameters `v`, `ewsc`, and `bc` control verbosity, erasures-without-corruption, and beyond-capacity testing. `Tab[]` lists code configurations. `struct wspace` holds sent/received codewords, syndrome, correction buffer, and error location arrays.

Control flow: `run_exercise()` initializes an RS control, allocates workspace, and tests several padding levels. `get_rcw_we()` creates a random codeword, encodes parity, injects random errors and erasures, and records true locations. `exercise_rs()` tests correction-buffer, caller-syndrome, and in-place decode paths up to correction capacity. `exercise_rs_bc()` injects beyond-capacity patterns and checks that any successful decode still yields a valid codeword.

State and persistence: workspace and RS controls are allocated per test configuration and freed. The module returns `-EAGAIN` after running so it unloads directly.

Dependencies/integration: depends on `rslib`, random numbers, module params, and slab allocation. It exercises `encode_rs16()` and `decode_rs16()`.

Risks/test signals: randomized tests can be expensive for small fields with high trial counts. It reports wrong data, wrong return values, wrong error positions, and silent beyond-capacity failures, then logs overall pass/fail.
