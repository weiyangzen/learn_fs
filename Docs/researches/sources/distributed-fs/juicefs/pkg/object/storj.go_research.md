# sources/distributed-fs/juicefs/pkg/object/storj.go

Purpose: implements a Storj DCS/uplink object storage backend behind `storj`.

Important APIs and types: `storjClient` holds an `uplink.Project` and bucket. It implements `Shutdown`, CRUD, list, multipart begin/upload/commit/abort/list, and `storjBackoff` for rate-limit retries.

Control flow and state: `storjBackoff` retries `uplink.ErrTooManyRequests` with exponential delays and respects context cancellation. `Put` retries only when the input is seekable, rewinding to the captured start position. `List` compensates for uplink ordering and prefix semantics by broadening the prefix, filtering client-side, deduplicating prefix entries, sorting, and truncating to `limit`. Multipart upload commits parts by upload ID rather than passing a part list.

Persistence and integration: persistent state is in a Storj bucket opened from an access grant. `newStorj` requires the access grant via access-key argument and bucket name in endpoint, sets `UserAgent`, opens the project, and registers in `init`.

Risks and test signals: list pagination ignores `token` and uses start-after style filtering; returning `hasMore` depends on `generateListResult` after client truncation. Non-seekable puts cannot be retried safely. No Storj-specific tests are present.
