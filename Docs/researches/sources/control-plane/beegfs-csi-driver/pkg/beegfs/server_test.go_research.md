# sources/control-plane/beegfs-csi-driver/pkg/beegfs/server_test.go

Purpose: Verifies that shared logging infrastructure redacts sensitive BeeGFS configuration values before they reach klog output.

Important APIs/types/functions: `TestStripSecretsFromLogs` configures klog flags to write verbose logs to a buffer, creates a `beegfsv1.BeegfsConfig` with `ConnAuth` and `TLSCert`, then calls `LogError`, `LogDebug`, and `LogVerbose`.

Control flow: The test initializes a fresh flag set for klog, sets verbosity to include all tested log levels, disables stderr logging, captures output in a bytes buffer, and checks after each log call that the plaintext secret is absent and the redaction marker appears.

State and persistence: Mutates global klog configuration and output for the process. Uses in-memory buffer only.

Dependencies and integration points: Depends on BeeGFS operator API JSON/marshal redaction behavior and the server logging helpers. It protects `logGRPC` and other service logs indirectly because they use the same logging path.

Risks: Global klog state can interact with other tests if run in the same package and order-dependent settings leak. The test checks one secret string and one redaction marker, not every sensitive field or every logged request type.

Test signals: Strong targeted signal that `ConnAuth` is not emitted in plaintext at error, debug, or verbose levels and that redaction remains visible.
