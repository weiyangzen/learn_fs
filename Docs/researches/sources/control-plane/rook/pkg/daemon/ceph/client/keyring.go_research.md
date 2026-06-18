# sources/control-plane/rook/pkg/daemon/ceph/client/keyring.go

Purpose: generates and writes Ceph keyring content for admin and non-admin users, creates keys through Ceph auth APIs, and validates base64-encoded key strings.

Important APIs: `AdminKeyringTemplate` includes broad `allow *` caps for mds, mon, osd, and mgr. `UserKeyringTemplate` emits a minimal user section. `CephKeyring()` chooses the template based on `AdminUsername`. `CreateKeyring()` calls `AuthGetOrCreateKey()` with desired caps and writes generated content. `WriteKeyring()` creates parent dirs with 0700 and writes keyring files with 0600. `IsKeyringBase64Encoded()` decodes with standard base64 and logs on failure.

Control flow and persistence: this file writes secret material to disk and relies on caller-provided paths. `GenerateConnectionConfigWithSettings()` in `config.go` uses `WriteKeyring()` for the connection keyring. `CreateKeyring()` mutates Ceph auth state if the key does not exist and persists the resulting keyring locally.

Dependencies and integration: depends on auth helpers from other client files, `os`, `filepath`, and shared logger. Risks include sensitive key material in memory and files, overly broad admin capabilities, incorrect username qualification if callers pass unqualified non-admin names, and logging base64 decode errors for invalid secret data. No direct tests are present in this subset; indirect coverage comes from config generation writing keyrings.
