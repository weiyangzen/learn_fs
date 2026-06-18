# sources/distributed-fs/juicefs/pkg/object/bunny.go


Purpose: implements the optional Bunny.net Storage backend behind the `bunny` build tag and registers it as `bunny`. It adapts `github.com/l0wl3vel/bunny-storage-go-sdk` to JuiceFS `ObjectStorage`.

Important APIs and flow: `bunnyClient` embeds `DefaultObjectStorage`, so unsupported operations use shared defaults. `Get` uses `DownloadPartial` with an inclusive end offset, mapping `limit == -1` to `math.MaxInt64`; `Put` buffers the entire reader and uploads with overwrite enabled; `Delete` ignores Bunny `"Not Found"` errors; `Head` calls `Describe`; `List` only supports delimiter `/`, lists a parent directory, filters by prefix and marker, and returns `generateListResult`.

State and persistence: all data lives in Bunny Storage. This adapter keeps only endpoint and SDK client state. Directory identity is represented by trailing `/` in normalized object names.

Dependencies and integration: depends on Bunny's SDK and JuiceFS helpers `obj`, `generateListResult`, and `notSupported`. `newBunny` normalizes endpoints to `https://...` and uses the password argument as the storage-zone password.

Risks: `Put` and `Get` read whole objects into memory, so large objects are risky. Error handling compares string messages. Context cancellation is not propagated to the Bunny SDK calls. Listing is single-directory oriented and does not use a server continuation token.

Test signals: `object_storage_test.go` contains a Bunny test skeleton, but it is commented out, so this backend has little automated coverage unless built and tested manually with `bunny` tags and credentials.
