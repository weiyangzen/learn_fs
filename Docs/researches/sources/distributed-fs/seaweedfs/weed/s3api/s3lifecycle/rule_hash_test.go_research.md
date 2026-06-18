# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/rule_hash_test.go

## Purpose
This file verifies the stability and semantic sensitivity of `RuleHash`, especially around fields that determine lifecycle action identity and bootstrap/event-driven state continuity.

## Important APIs and test cases
Tests call `RuleHash` with constructed `Rule` values. They cover deterministic repeat hashing, tag map order invariance, prefix trailing slash significance, ID/status ignoring, different days/action kinds/filter fields, nil handling, and collision resistance against naive delimiter encodings.

## Control flow and state behavior under test
The tests establish that operational state should survive rule renames and enable/disable flips because those fields are not hashed. They also establish that prefix, tags, size filters, and action parameters must change the hash because they alter the object/action match set. Collision-resistance tests use embedded `=`, newline, and separator-like prefix strings to ensure length-prefix and field-tag encoding isolates fields.

## Dependencies and integration points
The file depends only on the local lifecycle package and Go testing. It protects consumers such as `engine.ActionKey`, scheduler prior-state maps, and router matches from subtle hash instability or accidental state reuse.

## Risks and gaps
The tests do not prove cryptographic collision absence for the truncated eight-byte digest. They also only cover fields currently present in `Rule`; future fields need corresponding test additions.

## Test signals
These tests are strong evidence that the current hash encoding has intentional compatibility semantics and is safe against common delimiter-forgery regressions.
