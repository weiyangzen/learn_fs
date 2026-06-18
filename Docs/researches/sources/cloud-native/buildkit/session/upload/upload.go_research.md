## sources/cloud-native/buildkit/session/upload/upload.go

Purpose: client-side helper for pulling upload content from a session provider and writing it to an `io.Writer`.

Important APIs/types/functions: `New(ctx, c, url)` builds outgoing metadata from URL path and host, opens an `Upload.Pull` bidirectional stream on the session caller connection, and returns `*Upload`. `Upload.WriteTo(w)` receives `BytesMessage` chunks until EOF and writes them to `w`, returning the byte count.

Control flow: `New` derives the session context through `c.Context`, attaches metadata keys `urlpath` and `urlhost`, creates a client from `c.Conn`, and calls `Pull`. `WriteTo` loops on `RecvMsg`; EOF is successful completion, other errors are wrapped, and writer errors return with the bytes written so far.

State and persistence: `Upload` stores only the active gRPC stream. No content is buffered beyond one message.

Dependencies and integration points: pairs with `uploadprovider.Uploader` and generated upload stubs. Used when BuildKit needs client-provided HTTP-like response bodies through the session.

Risks and test signals: short writes are counted but not retried; it trusts `io.Writer` contract that non-nil error accompanies incomplete writes. The `keyHost` metadata is set but provider code in this subset only consumes path. No direct test appears in this subset.
