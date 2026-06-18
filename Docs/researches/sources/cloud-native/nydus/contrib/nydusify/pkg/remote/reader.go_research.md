# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader.go

Purpose: adapts containerd remote fetchers and the local `Remote` wrapper into content `ReaderAt` and `ReadSeekCloser` interfaces.

Important APIs/types/functions: `FromFetcher`, `fetchedProvider`, `readerAt`, `readerAt.ReadAt`, `readerAt.Size`, `Remote.ReaderAt`, and `Remote.ReadSeekCloser`.

Control flow: `FromFetcher` returns a content provider whose `ReaderAt` fetches a descriptor and wraps the returned reader. `readerAt.ReadAt` seeks when the requested offset differs from its tracked offset, then reads until the caller buffer is full or an error occurs. `Remote.ReaderAt` and `ReadSeekCloser` derive the request ref, instantiate a fresh resolver/fetcher, and either wrap fetched content or require the returned reader to implement `io.ReadSeekCloser`.

State and persistence: `readerAt` tracks current offset and size in memory. No data is persisted.

Dependencies and integration points: containerd content/remotes, OCI descriptors, and registry fetchers that support seeking/range reads.

Risks and test signals: `ReadAt` fails if the fetcher returns a non-seekable reader and a non-current offset is requested. The offset state is not concurrency-safe; `ReaderAt` should not be shared across concurrent reads without synchronization.
