# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect.go

This file initializes IBM Key Protect as a KMS backend.

It defines provider type `ibmkeyprotect`, configuration keys for service API key, instance ID, base URL, and token URL, plus mandatory connection/token detail slices and sentinel errors for missing required values. `InitKeyProtect()` reads required API key and instance ID using `GetParam()`, defaults base URL and token URL to IBM client defaults when omitted, constructs a `kp.ClientConfig` with verbose logging, and calls `kp.New()`. `IsIBMKeyProtect()` is the provider predicate on `Config`.

State is the constructed IBM Key Protect client configuration; the file does not persist secrets itself. Dependencies include `github.com/IBM/keyprotect-go-client`, Rook KMS config helpers, and wrapped sentinel errors. Integration points include `envs.go`, which ensures the API key is mounted from a Kubernetes Secret rather than left in literal connection details, and `encryption.go`, which injects the API key into runtime config for OSD-side KMS access.

Risks include verbose client logging, reliance on caller-provided API key handling, and no live network validation during construction. `ibm_key_protect_test.go` covers missing required fields and default/custom URL behavior.
