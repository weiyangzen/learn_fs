# sources/cloud-native/stargz-snapshotter/cmd/stargz-store/helper/main.go

Purpose: Small helper binary that reads credential JSON from stdin and sends it to a running `stargz-store` controller socket.

Important API: `main`.

Control flow: It chooses the Unix socket address from argv or defaults to `/var/lib/stargz-store/store.sock`, reads all stdin, builds a gRPC client using containerd's Unix dialer, insecure local credentials, backoff configuration, and containerd default message sizes, then calls `Controller.AddCredential`.

State and persistence: No local persistence. It transmits credential data to the store daemon, which merges it into an in-memory keychain.

Dependencies and integration: Uses containerd defaults/dialer and generated store protobuf client.

Risks: Uses `panic` for all errors, appropriate for a helper but rough for UX. Reads all stdin into memory. Does not close the gRPC connection explicitly. Credentials are passed over a local Unix socket without extra authentication.

Test signals: No direct tests.
