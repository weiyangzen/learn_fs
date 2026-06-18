# sources/cloud-native/cri-o/server/utils_test.go

## Purpose
Unit tests for selected server utility helpers.

## Important APIs, Types, And Functions
`TestMergeEnvs`, `TestGetDecryptionKeys`, and `TestGetSourceMount`.

## Control Flow
`TestMergeEnvs` covers Kubernetes override precedence, nil image or kube env inputs, empty kube keys, invalid image env strings, and empty values. `TestGetDecryptionKeys` generates an RSA key, writes it to a temp directory, and calls `getDecryptionKeys`. `TestGetSourceMount` validates longest-prefix mountpoint selection and expected errors.

## State And Persistence
Creates temp key files and in-memory mount info. No persistent repository state.

## Dependencies And Integration Points
Uses Go testing, crypto/x509 key material, OCI image spec, CRI types, and containers/storage mount info.

## Risks And Test Signals
Env test compares as a set, so order regressions may be missed even though container env order can matter. Decryption-key assertion condition appears weak because it fails only if both `err != nil` and `cc != nil`. Symlink rejection and missing-directory behavior are not covered.
