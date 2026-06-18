# sources/cloud-native/containerd/core/content/proxy/content_writer.go

Purpose: remote content writer backed by a bidirectional content write stream.

Important type/methods: `remoteWriter` tracks ref, stream client, offset, and digest. `send` performs synchronous request/response exchange and updates digest from responses. `Status`, `Digest`, `Write`, `Commit`, `Truncate`, and `Close` implement `content.Writer`.

Control flow and state: `Write` chunks input into half of `defaults.DefaultMaxSendMsgSize`, sends `WRITE` requests with the current offset, updates offset based on server response, and returns `io.ErrShortWrite` if the server advances less than the sent chunk. `Commit` applies content opts to collect labels, sends `COMMIT`, validates size and digest when provided, updates local state, and always closes the stream in a defer. `Truncate` only adjusts the local offset until a later write/commit validates it remotely.

Dependencies and integration: content service API, errgrpc, default message-size constants, protobuf time conversion, go-digest.

Risks: `Write` returns `0` on the first chunk send error even if previous chunks in the same call succeeded, because the error branch does not return accumulated `n`. `Truncate` is optimistic. Commit closes the stream even on error, so callers needing retry must open a new writer.

Test signals: no direct unit tests here; content testsuite can expose status, resume, commit, and short-write behavior when run through the proxy.
