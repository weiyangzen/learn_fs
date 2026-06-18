# sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.cc

## Purpose
`rgw_policy_s3.cc` parses and evaluates S3 browser-upload POST policies. It validates expiration, exact-match and prefix conditions, content-length ranges, and ensures request variables are represented in policy conditions.

## Important APIs, Types, And Functions
Internal `RGWPolicyCondition` resolves literal or `$variable` operands through `RGWPolicyEnv` and delegates to derived checks. Implementations are `RGWPolicyCondition_StrEqual` and `RGWPolicyCondition_StrStartsWith`. `RGWPolicyEnv` stores case-insensitive variables. `RGWPolicy` implements `set_expires()`, `add_condition()`, `check()`, and `from_json()`.

## Control Flow
`from_json()` parses a bufferlist as JSON, requires `expiration`, parses ISO8601 time, requires `conditions`, and accepts either three-element condition arrays or simple object equality checks. `add_condition()` handles `eq`, `starts-with`, and `content-length-range`, updating min/max length for the latter. `check()` rejects expired policies, verifies simple checks, evaluates conditions, and finally asks the environment whether every non-ignored, non-checksum variable was covered.

## State And Persistence
Policy objects are in-memory request validators. They retain expiration string/time, condition pointers, simple checks, checked variable names, and min/max content length. No policy is persisted by this file.

## Dependencies And Integration Points
It depends on Ceph JSON parsing, clock/time parsing, string helpers, sanitized logging for policy values, checksum header recognition, and POST object request handling from `rgw_op.h`/protocol subclasses.

## Risks And Test Signals
Risks include manual ownership of condition pointers, overly strict missing-condition checks, variable case handling, time parsing, length bounds, and malformed JSON arrays. Tests should cover expired policies, valid/invalid `eq` and `starts-with`, content-length range narrowing, `$variable` resolution, ignored/checksum variables, malformed condition arrays, and sanitized logging paths.
