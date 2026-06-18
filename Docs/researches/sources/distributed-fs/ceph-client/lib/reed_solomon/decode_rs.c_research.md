## sources/distributed-fs/ceph-client/lib/reed_solomon/decode_rs.c

Purpose: generic Reed-Solomon decoder body included by 8-bit and 16-bit wrappers in `reed_solomon.c`.

Important functions/data: it operates on `struct rs_control`, `struct rs_codec`, caller data/parity/syndrome/erasure arrays, and decoder scratch buffers embedded in `rs_control` (`lambda`, `syn`, `b`, `t`, `omega`, `root`, `reg`, `loc`).

Control flow: it validates padding, uses caller-provided syndromes if present, otherwise computes syndromes over data and parity, converts to index form, and returns early for zero syndrome. It initializes the erasure locator, runs Berlekamp-Massey to compute the error+erasure locator polynomial, performs Chien search for roots/locations, computes the evaluator polynomial omega, calculates correction values, verifies the correction syndrome against the received syndrome, then either fills `corr`/`eras_pos` or applies corrections in place to data/parity.

State and persistence: decoder scratch buffers are stored in `rs_control`, so callers must serialize decode calls per control object. The input codeword may be modified in place when no correction buffer is provided.

Dependencies/integration: included inside `decode_rs8()` and `decode_rs16()` wrappers. Uses GF lookup tables and `rs_modnn()`.

Risks/test signals: invalid erasure positions, excessive errors, deg/root mismatches, and syndrome verification failures return `-EBADMSG`. `test_rslib.c` tests correction-buffer, caller-syndrome, in-place, erasure, padding, and beyond-capacity behavior.
