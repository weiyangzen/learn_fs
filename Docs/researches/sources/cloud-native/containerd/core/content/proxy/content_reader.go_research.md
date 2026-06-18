# sources/cloud-native/containerd/core/content/proxy/content_reader.go

Purpose: remote `content.ReaderAt` implementation backed by the content service streaming read API.

Important type/methods: `remoteReaderAt` stores parent context, digest, size, and a `TTRPCContentClient`. `Size` returns known size. `ReadAt` sends `ReadContentRequest` with digest, offset, and requested size, receives stream chunks, and fills the caller buffer. `Close` is a no-op.

Control flow and state: each `ReadAt` call opens a child context and cancels it to avoid gRPC stream goroutine leaks, then repeatedly `Recv`s until the buffer is filled or an error occurs. State is immutable except local counters.

Dependencies and integration: used by `proxyContentStore.ReaderAt`. Depends on content service API and go-digest.

Risks: it does not specially translate EOF semantics; remote stream errors propagate directly. If the server returns more bytes than remaining buffer, extra bytes are ignored by `copy`, but the loop exits once the requested buffer is filled. The parent context lifetime controls all future reads.

Test signals: no direct tests here; behavior is indirectly covered by content store tests against the proxy implementation where present.
