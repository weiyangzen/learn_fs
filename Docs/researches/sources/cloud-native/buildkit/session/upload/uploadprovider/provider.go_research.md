## sources/cloud-native/buildkit/session/upload/uploadprovider/provider.go

Purpose: session attachable that lets the daemon pull one-shot `io.ReadCloser` payloads registered by the client.

Important APIs/types/functions: `New` creates an `Uploader` with an id-to-reader map. `Uploader.Add(r)` generates an identity id, stores the reader, and returns an `http://buildkit-session/<id>` URL. `Register` registers the upload gRPC service. `Pull(stream)` resolves the id from incoming `urlpath` metadata, removes the reader from the map, streams it with `io.Copy`, and closes it. `writer.Write` sends data as upload `BytesMessage` chunks capped at 3 MiB.

Control flow: `Pull` reads metadata, uses `path.Base` to get id, locks the map, returns an error for missing ids, deletes the id before streaming to enforce one-shot semantics, then copies and closes.

State and persistence: in-memory map of pending readers. Intended state is transient and consumed exactly once.

Dependencies and integration points: pairs with `upload.New`. Uses BuildKit identity generation and gRPC metadata.

Risks and test signals: `Add` writes to the map without taking `mu`, while `Pull` reads/deletes with `mu`; concurrent `Add`/`Pull` would race. Since ids are removed before successful copy, failed streams cannot be retried. No direct test is in this subset.
