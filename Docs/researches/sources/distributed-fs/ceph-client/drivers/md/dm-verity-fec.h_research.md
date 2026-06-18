# sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.h

## Purpose
`dm-verity-fec.h` declares the optional dm-verity forward-error-correction interface, its target-table option names, Reed-Solomon parameter bounds, persistent FEC configuration, and per-bio FEC state.

## Important APIs, Types, and Functions
The header defines `DM_VERITY_FEC_RS_N`, minimum/maximum roots, deinterleave buffer sizing, option strings, `struct dm_verity_fec`, and `struct dm_verity_fec_io`. When `CONFIG_DM_VERITY_FEC` is enabled it declares `verity_fec_decode()`, `verity_fec_status_table()`, `verity_fec_finish_io()`, `verity_fec_init_io()`, option parsing, destructor, and constructor helpers. When disabled it supplies stubs.

## Control Flow
The main dm-verity target calls `verity_fec_ctr_alloc()` early, lets optional argument parsing populate `v->fec`, calls `verity_fec_ctr()` after hash tree setup, initializes per-bio FEC state with `verity_fec_init_io()`, invokes `verity_fec_decode()` only after verification failures, and calls `verity_fec_finish_io()` when completing each bio.

## State and Persistence Behavior
FEC configuration is runtime state derived from the target table and parity device. `corrected` is an atomic runtime counter. Per-bio state stores Reed-Solomon control data, erasure indexes, output buffer, recursion level, number of allocated buffers, and flexible-array deinterleave buffers. The header does not define on-disk format; it describes how existing parity blocks are consumed.

## Dependencies and Integration Points
The header includes `dm-verity.h` and Linux rslib. It is tightly coupled to the dm-verity target's block geometry, hash validation, and per-IO data lifecycle. Compile-time stubs allow the main target to parse and build without FEC support.

## Risks and Test Signals
Tests should cover both configured and unconfigured builds. Enabled builds need option-count accounting, FEC-enabled predicate behavior, per-bio initialization/finish idempotence, and correct propagation of `-EOPNOTSUPP` or `-EINVAL` from disabled stubs.
