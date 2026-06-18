# sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.h

## Purpose
`rgw_policy_s3.h` declares the in-memory environment and policy evaluator for S3 POST policy validation.

## Important APIs, Types, And Functions
`RGWPolicyEnv` exposes `add_var()`, `get_var()`, `get_value()`, and `match_policy_vars()` over a case-insensitive variable map. `RGWPolicy` exposes `set_expires()`, `set_var_checked()`, `add_condition()`, `add_simple_check()`, `check()`, and `from_json()`, plus public `min_length` and `max_length` fields.

## Control Flow
The header defines a two-stage pattern: parse JSON into `RGWPolicy`, populate `RGWPolicyEnv` from request fields, then call `check()` to validate both explicit conditions and coverage of request variables.

## State And Persistence
`RGWPolicy` owns condition pointers and request-independent parsed policy state. It is not persisted by the header; it is constructed per policy validation.

## Dependencies And Integration Points
It depends on `rgw_string.h` for case-insensitive comparators and Ceph bufferlist declarations. `RGWPostObj` implementations are the primary consumers.

## Risks And Test Signals
Risks include public mutable length fields, pointer ownership, and the need to call `from_json()` before `check()`. Tests should validate parser/evaluator lifecycle and destructor cleanup under parse failures.
