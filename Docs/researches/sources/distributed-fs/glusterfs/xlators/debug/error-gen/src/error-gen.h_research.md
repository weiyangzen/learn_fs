# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.h

## Purpose
Declares the private state and errno-table shape used by the `debug/error-gen` translator. It also defines the translator's pseudo-error range for behavior that cannot be represented by a normal `-1, op_errno` result.

## Important APIs, types, and functions
`GF_FAILURE_DEFAULT` is a legacy default percentage constant. `enum GF_PSEUDO_ERRORS` currently defines `GF_ERROR_SHORT_WRITE = 1000`, used to make `writev` pass a smaller iovec rather than unwind with an errno. `eg_t` is the private xlator state: `enable[GF_FOP_MAXVALUE]`, `op_count`, `failure_iter_no`, `error_no_int`, `random_failure`, and `gf_lock_t lock`. `sys_error_t` stores an errno count and fixed-size errno array used by `error_no_list[]` in the C file.

## Control flow
The header does not implement behavior, but its fields directly drive `error_gen()`. `failure_iter_no` is deliberately overloaded: in legacy `random-failure` mode it is an operation interval, while in normal mode it is the numerator for the configured failure percentage against the C file's `FAILURE_GRANULARITY`.

## State and persistence behavior
All declared state is private in-memory translator state. It is allocated in `init()`, mutated by `reconfigure()` and FOP execution, exposed through statedump, and freed in `fini()`. No on-disk format or network serialization is defined here.

## Dependencies and integration points
Includes `error-gen-mem-types.h` for allocation tags and depends on GlusterFS core definitions brought in by the C file, especially `GF_FOP_MAXVALUE`, `gf_boolean_t`, and `gf_lock_t`. The pseudo-error constant is consumed by the `writev` failure path.

## Risks and test signals
The overloaded `failure_iter_no` name is easy to misuse when adding features. `sys_error_t.error_no[20]` assumes no FOP errno list grows beyond 20 entries. Future pseudo-errors need to stay outside platform errno ranges and must be handled explicitly by wrappers. Tests should cover the short-write pseudo-error and any change to FOP count or errno list sizes.
