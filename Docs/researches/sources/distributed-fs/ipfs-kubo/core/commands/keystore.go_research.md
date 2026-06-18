# sources/distributed-fs/ipfs-kubo/core/commands/keystore.go

## Purpose

`keystore.go` defines the `ipfs key` command tree for creating, importing, exporting, listing, renaming, removing, rotating, signing with, and verifying named libp2p/IPNS keys. It bridges user-facing command syntax to the Kubo CoreAPI key service for daemon-safe operations, and to direct filesystem repo access for commands that must work offline or without a running daemon.

## Important APIs, Types, and Functions

The root `KeyCmd` registers `gen`, `export`, `import`, `ls`, deprecated `list`, `rename`, `rm`, `rotate`, `sign`, and `verify`. Output structs are `KeyOutput`, `KeyOutputList`, `KeyRenameOutput`, `KeySignOutput`, and `KeyVerifyOutput`. Key-format constants distinguish `libp2p-protobuf-cleartext` from `pem-pkcs8-cleartext`; key type/size options are shared with CoreAPI key generation. `doRotate` is the direct repo mutation helper that backs up the old identity and writes a new identity into config. `DaemonNotRunning` checks repo locking before rotation.

## Control Flow

Most live key operations call `cmdenv.GetApi` and then `api.Key()` methods. `key gen` validates the requested name and type/size, creates a key, and formats its peer ID with the requested IPNS base. `key export` is `NoRemote`; it checks repo version, opens the filesystem keystore read-only, formats the private key bytes, and its CLI post-run writes a `0600` output file. `key import` reads a file/stdin, decodes PEM or libp2p protobuf, optionally rejects non-RSA/non-Ed25519 keys, opens the repo, checks for duplicate names, persists into the keystore, and emits the derived peer ID. Rename/remove/list delegate to CoreAPI. Rotate opens the repo directly after confirming the daemon is not running, stores the old identity under a user-supplied keystore name, and rewrites config identity. Sign/verify read data from file/stdin, use CoreAPI signing/verification, and multibase-encode or decode signatures.

## State and Persistence Behavior

Generated/imported/renamed/removed keys persist in the repo keystore. `export` emits private key material to a user-selected file but does not mutate repo state. `rotate` mutates both keystore and config identity and is intentionally local-only. Sign/verify are read-only except for transient data in memory. CLI text encoders escape non-printable key names but signatures and private key bytes must still be treated as sensitive.

## Dependencies and Integration Points

This file depends on `go-ipfs-cmds`, Kubo `cmdenv`, `coreiface/options`, repo/fsrepo and migrations, boxo keystore, libp2p crypto/peer, multibase, Go `x509`/`pem`, and `keyencode` for IPNS base selection. It integrates with `ipfs name publish` through generated key names and peer IDs, and with repo migration/version compatibility through `fsrepo.RepoVersion`.

## Risks and Test Signals

High-risk behavior includes exporting cleartext private keys, importing arbitrary key types with `--allow-any-key-type`, direct repo locking during rotate/import/service operations, and PEM/std-key conversion edge cases for Ed25519 pointer/value handling. Tests should cover duplicate names, the protected `self` name, repo version mismatch on export, default output file permissions, PEM hints on wrong import format, disallowed key types, rotate with daemon lock present, signature round trips, multibase decode errors, and IPNS base formatting.
