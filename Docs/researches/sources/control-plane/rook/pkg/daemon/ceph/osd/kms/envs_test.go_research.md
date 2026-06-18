# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs_test.go

This test file validates KMS environment-variable translation and reverse scanning.

`TestVaultTLSEnvVarFromSecret` checks Vault without TLS, Vault with TLS, and IBM Key Protect env generation. It asserts sorted envs, Vault default backend path, secret-backed Vault token, Vault TLS file path translation, and secret-backed IBM API key. `TestConfigEnvsToMapString` verifies that unrelated environment variables are ignored, `KMS_PROVIDER` is included, Vault-prefixed variables are collected, and the resulting map marks KMS as enabled in a ClusterSpec. `TestVaultConfigToEnvVar` table-tests exact env lists for Vault default/custom backend, Vault TLS, IBM API key removal from literal values, and KMIP token-detail removal with `KMIP_` prefixing.

State is process environment managed through `t.Setenv` and in-memory specs. Dependencies include Ceph API KMS predicates and Kubernetes `EnvVar` structures.

Risks surfaced include deterministic ordering and avoiding secret leakage through literal env values. Gaps include Azure env generation, multiple Vault TLS options beyond CACERT, mutation side effects on reused specs, and `ConfigEnvsToMapString()` behavior when KMIP-prefixed and unprefixed keys collide.
