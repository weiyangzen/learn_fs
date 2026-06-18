# Research: sources/distributed-fs/seaweedfs/weed/s3api/policy/postpolicyform.go

## sources/distributed-fs/seaweedfs/weed/s3api/policy/postpolicyform.go

Purpose: parser and evaluator for Amazon S3 POST Object policy documents. It is derived from MinIO code and validates policy JSON conditions against multipart form headers.

Important APIs: `ParsePostPolicyForm` unmarshals expiration and conditions, normalizes map conditions to `eq`, parses `eq`, `starts-with`, and `content-length-range`, and rejects malformed/non-string fields. `CheckPostPolicy` verifies expiration, builds exact X-Amz policy keys and prefix-stem rules, rejects extra non-reserved `X-Amz-*` form fields, enforces every matching prefix-stem value prefix, then evaluates each declared condition. `startsWithConds` lists known S3 condition keys and whether `starts-with` is allowed. `postPolicyAuthFields` permits required SigV4 form fields without explicit conditions.

State and persistence: no persistence; `PostPolicyForm` stores parsed expiration, condition policies, and content-length range. Dependencies are JSON, HTTP header canonicalization, reflection for errors, string/time/strconv helpers. Integration points are S3 POST upload handlers. Risks: `content-length-range` is parsed but not enforced in `CheckPostPolicy` here, so callers must enforce size separately or this is incomplete; canonical header casing matters; prefix-stem conditions can overlap and are intentionally all enforced. Tests cover unknown keys, extra X-Amz fields, reserved auth fields, exact/prefix matching, and error context.
