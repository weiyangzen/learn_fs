## sources/distributed-fs/ceph-client/lib/reed_solomon/encode_rs.c

Purpose: generic Reed-Solomon encoder body included by the 8-bit and 16-bit encoder wrappers in `reed_solomon.c`.

Important behavior: it uses `struct rs_control` and its shared codec tables (`alpha_to`, `index_of`, `genpoly`) to update a caller-provided parity array. The body is type-generic because it is included inside wrappers whose `data` pointer type differs.

Control flow: the function validates `len` by computing `pad = nn - nroots - len`, rejecting out-of-range values with `-ERANGE`. For each input symbol, it computes feedback from the masked/inverted data byte and current first parity element. If feedback is nonzero, it XORs generator-polynomial contributions into parity positions. It then shifts the parity vector with `memmove()` and writes the final feedback contribution or zero.

State and persistence: the caller owns and initializes `par`; the encoder mutates it cumulatively. No file-local persistent state exists.

Dependencies/integration: included in `encode_rs8()` and `encode_rs16()`, which export the public kernel APIs. Depends on precomputed GF tables and `rs_modnn()`.

Risks/test signals: parity must be initialized by the caller, usually to zero. Incorrect `invmsk` or length/padding produces wrong codewords. `test_rslib.c` validates generated parity by round-trip decode and by re-encoding returned words in beyond-capacity tests.
