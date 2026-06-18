# sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_user_tags_test.go

## Purpose

This file provides focused coverage for embedded IAM user tag operations: `TagUser`, `ListUserTags`, and `UntagUser`. It verifies AWS query-encoded tag inputs mutate `iam_pb.Identity.Tags` correctly, response XML can be unmarshaled into shared IAM response types, validation errors map to expected IAM codes, and tag limits are enforced.

## Important APIs, types, and helpers

`postTagAction` sends a form-encoded POST through a test mux router bound to `EmbeddedIamApiForTest.DoActions`. It sets `PostForm`, `Form`, and `Content-Type`, making it suitable for hand-built tag edge cases that are awkward to express with the AWS SDK. `findIdentity` searches an `iam_pb.S3ApiConfiguration` by name so tests do not assume identity ordering.

The tests reuse the fixture and error parsers from `s3api_embedded_iam_test.go`. AWS SDK request builders are used for normal `TagUser`, `ListUserTags`, `UntagUser`, and not-found request shape; hand-built `url.Values` are used for duplicate, empty, limit, and malformed member parameters.

## Control flow and coverage

`TestEmbeddedIamTagUser` creates an `alice` identity, sends two tags through the AWS SDK, and asserts both tags are persisted in order with expected key/value pairs. `TestEmbeddedIamListUserTags` seeds `bob` with tags and confirms the response contains both tags and `IsTruncated=false`. `TestEmbeddedIamUntagUser` removes one existing tag and one missing tag, asserting the missing key is ignored and only the requested existing key is removed.

Validation tests cover a too-long tag key returning `ValidationError`, replacement of an existing tag value without duplicating the tag, exceeding `MaxUserTags` returning `LimitExceeded`/HTTP 403, no-op untag for a missing key, duplicate tag keys in a single request returning `InvalidInput`, invalid untag key cases, and `TagUser` against a missing user returning `NoSuchEntity`.

## State and persistence behavior

All tested state is on `iam_pb.Identity.Tags` within `api.mockConfig`, persisted through the normal `DoActions` and `ExecuteAction` changed-config path. `TagUser` merges new tags into existing tags, preserving prior order and replacing duplicate existing keys. `UntagUser` filters the tag slice and leaves unknown keys untouched. `ListUserTags` is read-only and does not mutate the config.

The tests assert in-memory fixture state after API calls, which confirms that the configuration save/load hook preserves tag fields. Since the fixture uses memory-backed persistence, it validates protobuf state behavior rather than a specific external store.

## Dependencies and integration points

This file depends on the main embedded IAM test fixture, AWS SDK IAM tag request builders, Gorilla mux, `iam_pb.UserTag`, shared IAM response aliases, `MaxUserTags`, `MaxUserTagKeyLength`, and IAM error constants. It integrates with the tag parsing helpers and dispatcher cases in `s3api_embedded_iam.go`.

## Risks and gaps

The tests do not cover maximum tag value length directly, empty tag value acceptance, sparse `Tags.member.N` numbering, `ListUserTags` for missing users, `UntagUser` missing users, or persistence behavior in non-memory stores. They also do not exercise auth/permission checks around tag APIs; the requests are routed straight to `DoActions` without `AuthIam` middleware.

Because `postTagAction` sets both `PostForm` and `Form`, it can bypass some parsing failure modes that would occur with malformed HTTP bodies. AWS SDK tests cover standard encoding, while hand-built tests mainly cover parser logic after form values exist.

## Test signals

The file strongly signals that user tags are bounded to 50 entries, tag keys are bounded to 128 characters, duplicate keys inside a request are rejected, existing keys are replaced rather than duplicated, unknown untag keys are ignored, and tag list pagination is intentionally not implemented because the bounded tag set fits in one response.
