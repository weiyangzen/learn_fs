# sources/control-plane/rook/pkg/operator/ceph/object/config.go

## Purpose
`config.go` builds RGW daemon configuration: frontend port/TLS strings, cephx keyrings, Keystone authentication settings, and monitor config-store options for a CephObjectStore.

## Important APIs, Types, and Functions
`clusterConfig.portString()` maps object-store gateway settings to beast frontend port, TLS cert, and private-key arguments, using internal port `8080` when not host-networked. `rgwFrontendStr()` adds `ssl_options`, TLS 1.2 ciphers, TLS 1.3 ciphersuites, and TLS groups. `buildSSLOptions()` converts `SslOptionsSpec` booleans into Ceph beast option tokens. `generateCephXUser()` derives the `client.rgw...` user, and `generateKeyring()` creates or rotates a daemon key via `keyring.SecretStore`. `generateMonConfigOptions()` builds RGW monitor options for sync, usage logs, zone metadata, Keystone, S3, Swift, user overrides, and secret-backed overrides. `configureKeystoneAuthentication()` and `mapKeystoneSecretToConfig()` validate Keystone secrets and map OpenStack-style environment keys into RGW config.

## Control Flow, State, and Persistence
Frontend strings are pure transformations. Keyring generation persists Kubernetes Secrets and optionally rotates Ceph auth keys when `shouldRotateCephxKeys` is set. Monitor config is persisted with `monStore.SetAll()` under the RGW cephx identity and deleted with `DeleteDaemon()`. Secret-backed RGW config values are read at reconcile time from the cluster namespace.

## Dependencies and Integration Points
This file connects CephObjectStore CRD fields, Ceph monitor config database helpers, cephx keyring helpers, Kubernetes Secrets, Keystone auth, S3/Swift protocol knobs, and RGW deployment generation in `rgw.go`.

## Risks and Test Signals
Risks include invalid user-supplied `RgwConfig` overriding operator defaults, secret selector errors blocking reconciliation, Keystone validation only accepting password/v3 with matching domains, and TLS option strings requiring exact Ceph syntax. Tests cover port formatting, TLS options/ciphers/groups, cephx user names, default and override mon config, and secret-sourced RGW config.
