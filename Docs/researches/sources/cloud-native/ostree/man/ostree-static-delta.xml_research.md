# sources/cloud-native/ostree/man/ostree-static-delta.xml

Purpose: This DocBook refentry defines the `ostree static-delta` manual page, documenting how users list, inspect, delete, generate, apply offline, and verify static delta files. Its most important contract is CLI semantics for `generate --to=REV`, optional `--from=REV`, `--empty`, `--max-usize`, and signature-related options.

Important APIs and commands: The documented subcommands are `list`, `show`, `delete`, `generate`, `apply-offline PATH [KEY-ID...]`, and `verify STATIC-DELTA [KEY-ID...]`. Signature API surface is user-facing rather than code-level: `--sign-type=ENGINE`, `--sign=KEY-ID`, positional `KEY-ID`, `--keys-file`, and `--keys-dir`. Engines documented here are `ed25519` and `dummy`; ed25519 keys are base64 encoded secret/public keys, while dummy keys are ASCII strings.

Control flow and state: The page describes a lifecycle: generate a delta from a source revision or from scratch to a target revision, publish/update repository metadata separately, then clients can apply or verify the delta. Persistent state is repository static delta content plus any signatures or key material. `--keys-dir` ties verification to a filesystem key hierarchy with well-known and revoked keys.

Dependencies and integration points: Integrates with repository revision resolution, static delta storage, summary metadata, offline delta application, signature verification engines, and file/dir based key discovery. It cross-links implicitly to `ostree summary` because generated deltas usually require summary refresh for distribution.

Risks: Documentation drift is high because signature engines and defaults evolve. The page describes key encodings but not operational key protection, revocation semantics, or concrete file format expectations for `--keys-dir`. The example is minimal and does not demonstrate generation or verification, so users may miss that summary metadata may need regeneration.

Test signals: Manual or integration tests should assert that documented options map to real CLI options, that ed25519 `--keys-file` accepts one base64 public key per line, that default sign type is still ed25519, and that generated deltas can be pulled with `--require-static-deltas`.
