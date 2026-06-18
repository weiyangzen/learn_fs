# sources/distributed-fs/beegfs-go/ctl/internal/util/url_test.go

Purpose: unit test for signed URL query generation.

Important APIs/types/functions: `TestURLEncodeSignMap`.

Control flow: builds a map containing capacity, meta/storage counts, net protocol, and UUID; signs using `uuid`; asserts no error and exact encoded output including `mac`.

State and persistence: none.

Dependencies and integration points: uses `testing`, `strconv`, and `stretchr/testify/require`.

Risks: exact string assertion is useful for determinism but will need updates if encoding/signature fields intentionally change. It does not cover missing key, special characters, duplicate keys, or empty maps.

Test signals: confirms deterministic query ordering and HMAC behavior for a representative input.
