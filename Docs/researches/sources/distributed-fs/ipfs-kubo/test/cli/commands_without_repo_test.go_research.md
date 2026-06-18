# sources/distributed-fs/ipfs-kubo/test/cli/commands_without_repo_test.go

Purpose: ensures repo-independent commands work when `IPFS_PATH` points at an uninitialized temporary directory.

Important APIs/functions: `TestCommandsWithoutRepo`, direct `exec.Command("ipfs", ...)`, and standard stdin/stdout assertions.

Control flow: subtests run `ipfs cid base32`, `cid format`, `cid bases`, `cid codecs`, `cid hashes`, and `multibase list/encode/decode/transcode` with only environment setup, then assert exact known outputs or expected registry entries.

State/persistence: no repo is initialized. Each command receives an isolated `IPFS_PATH` via `cmd.Env`.

Dependencies/integration: installed `ipfs` binary on PATH, repo-opening bypass for pure CID/multibase commands, multibase codec implementation, and CLI command classification.

Risks/test signals: catches accidental repo requirements in stateless commands. It uses direct OS execution rather than harness wrappers, so failures can reflect PATH/build environment problems.
