## sources/cloud-native/soci-snapshotter/config/fs.go

Purpose: defines filesystem/lazy-pull related configuration structs and normalization logic.

Important APIs/types/functions: `FSConfig`, `PrefetchConfig`, `BlobConfig`, `DirectoryCacheConfig`, `FuseConfig`, `BackgroundFetchConfig`, `RetryConfig`, `TimeoutConfig`, `ContentStoreConfig`, `TrimSocketAddress`, `parseFSConfig`, and nested parse functions.

Control flow: `parseFSConfig` fills defaults for mount timeout, FUSE metrics wait, max concurrency, and prefetch concurrency, then runs FUSE/background/HTTP/blob/content-store parsers. Blob retries inherit HTTP retry defaults. Content store defaults to SOCI and trims `unix://` from containerd addresses.

State and persistence: no direct state; config drives cache, FUSE, background fetch, content-store, and network behavior.

Dependencies and integration: daemon service config, cache config, resolver/fetch code, and store selection.

Risks and test signals: negative `PrefetchConfig.MaxConcurrency` is reset to default zero, while negative `MaxConcurrency` disables limits. Tests cover many defaults but not every normalization branch.
