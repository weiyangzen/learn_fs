# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs.go

This file translates KMS configuration between CephCluster specs, Kubernetes pod environment variables, and runtime environment maps.

`vaultTokenEnvVarFromSecret()` and `ibmKeyProtectServiceAPIKeyEnvVarFromSecret()` create secret-backed env vars for sensitive tokens. `vaultTLSEnvVarFromSecret()` maps Vault TLS secret names to mounted file paths under `/etc/vault`. `ConfigToEnvVar()` handles provider-specific transformations: default Vault backend path insertion, removal of IBM API key from literal connection details and replacement with secret-backed env var, KMIP token details exclusion with non-secret fields prefixed as `KMIP_`, generic env insertion, Vault token injection, TLS env insertion, and deterministic sorting. `ConfigEnvsToMapString()` scans process env for known KMS prefixes (`VAULT_`, `IBM_`, `KMIP_`, `AZURE_`) and `KMS_PROVIDER`, trimming the KMIP prefix when reconstructing config. `sortV1EnvVar()` keeps output stable.

State is environment variable lists/maps and mutates the input spec's connection details in some paths. Dependencies include Vault API constants, libopenstorage Vault defaults, Ceph API KMS predicates, Kubernetes env var types, and set utilities.

Risks include accidental mutation of caller maps, prefix collisions, leaking non-secret values, and relying on env scanning for OSD-side KMS reconstruction. `envs_test.go` covers sorting, Vault defaults/TLS/token, IBM secret-backed API key, KMIP secret exclusion, and env scanning.
