## sources/distributed-fs/ceph-client/lib/tests/liveupdate.c

### Purpose
This file is an in-kernel test helper for the liveupdate/LUO mechanism. It defines a small set of synthetic file-live-blocks (FLBs), registers them with a caller-provided `struct liveupdate_file_handler`, and verifies preserve/retrieve/finish callback plumbing by passing deterministic per-FLB magic handles through the liveupdate API.

### Important APIs, types, and functions
`TEST_NFLBS` creates three static `struct liveupdate_flb` instances in `test_flbs[]`. Each entry shares `test_flb_ops` and gets a distinct `compatible` string via `LIVEUPDATE_TEST_FLB_COMPATIBLE(i)`. `test_flb_preserve()` computes the FLB index by pointer subtraction against `test_flbs`, logs, and stores `TEST_FLB_MAGIC_BASE + index` in `argp->data`. `test_flb_retrieve()` validates the incoming `data` handle and stores it back as `argp->obj` on success. `test_flb_finish()` validates that `obj` matches the same magic value. `test_flb_unpreserve()` only logs. `liveupdate_test_register()` is the external integration function that initializes incoming data and registers each FLB on a supplied file handler.

### Control flow
`liveupdate_test_register()` first calls `liveupdate_test_init()`. Initialization is protected by a static `DEFINE_MUTEX(init_lock)` and static `initialized` flag using the cleanup-style `guard(mutex)` helper. The first call walks all test FLBs and invokes `liveupdate_flb_get_incoming()`, tolerating `-ENODATA` and `-ENOENT` while logging other errors. Registration then iterates through all FLBs with `liveupdate_register_flb(fh, flb)`, logs failures, and deliberately tries to register `test_flbs[0]` again to ensure duplicate registration returns `-EEXIST`.

### State and persistence
The only persistent runtime state is the static `initialized` latch and the static `test_flbs[]` table. The liveupdate payload is represented by numeric magic values in `argp->data`; no heap objects are allocated by this file. Across a live update, state enters through `liveupdate_flb_get_incoming()` and is validated by callback data matching.

### Dependencies and integration points
The file includes public liveupdate headers and `../../kernel/liveupdate/luo_internal.h`, making it closely coupled to the liveupdate implementation rather than a pure black-box test. It exports `liveupdate_test_register()` for other liveupdate test code or file handlers to call. It depends on module ownership via `.owner = THIS_MODULE` and normal kernel logging.

### Risks and edge cases
Pointer subtraction assumes every callback receives one of the statically declared `test_flbs`; a foreign FLB would produce an invalid index and magic value. The duplicate-registration check condition `if (!err || err != -EEXIST)` logs unless the result is exactly `-EEXIST`, which is intentional but easy to misread. Initialization logs incoming-data errors but does not fail registration, so a broken retrieve path may be visible only through logs.

### Test signals
Useful signals include preserve/retrieve/finish logs per compatible FLB, validation of deterministic magic data, duplicate registration producing `-EEXIST`, and non-fatal logging for unexpected incoming retrieval errors.
