## sources/cloud-native/moby/daemon/builder/backend/tag.go

**Purpose:** Parses and applies build tags after a successful classic build.

**Important APIs:** `tagImages` iterates normalized references, calls `ImageComponent.TagImage`, and prints success. `sanitizeRepoAndTags` normalizes raw tag strings, ignores empty entries, rejects digested references, applies default tags, and removes duplicates.

**Control flow:** Tag parsing uses `reference.ParseNormalizedNamed`, rejects `reference.Digested`, then canonicalizes through `reference.TagNameOnly`. Deduplication is based on the normalized string.

**State and persistence:** `tagImages` mutates daemon image tag state through `ImageComponent`. `sanitizeRepoAndTags` only creates an in-memory reference slice.

**Dependencies and integration:** Used by build backend after image creation. Depends on distribution reference parsing and daemon internal `image.ID`.

**Risks:** Digest-containing tags are rejected because build tags must be mutable names, not content addresses. Deduping after default-tag normalization prevents repeated tag writes.

**Test signals:** Should be covered by backend/tag unit tests or build API tests. Key cases are empty tags, duplicate tags, implicit `latest`, invalid references, and digest rejection.
