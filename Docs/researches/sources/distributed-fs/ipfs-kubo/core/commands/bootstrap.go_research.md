<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go

## Purpose

Implements `ipfs bootstrap` commands for listing, adding, and removing trusted bootstrap peer addresses in the repo config. It also handles the newer `auto` placeholder used by AutoConf-backed bootstrap expansion.

## Important APIs, Types, and Functions

`BootstrapCmd` defaults to `bootstrapListCmd` and exposes `add`, `rm`, and `rm all`. `BootstrapOutput` carries peer strings. `bootstrapAdd`, `bootstrapRemove`, and `bootstrapRemoveAll` mutate `config.Config.Bootstrap` and persist with `repo.SetConfig`. `bootstrapWritePeers` sorts output and prefixes `added` or `removed`.

## Control Flow

Command handlers parse body arguments, open the fsrepo from `cmdenv.GetConfigRoot`, load config, apply validation or AutoConf rules, then persist changed config. `add` normalizes `default` to `auto`, rejects adding `auto` when AutoConf is disabled, validates non-auto multiaddrs as transport plus `/p2p`, deduplicates, and prepends new entries. `rm` either removes all or parses requested bootstrap peers and removes matching peer IDs or addresses.

## State and Persistence Behavior

This file directly persists repo config changes. `bootstrapRemoveAll` clears `cfg.Bootstrap`; selective `rm` rewrites it through `cfg.SetBootstrapPeers`. `list --expand-auto` is read-only and returns resolved bootstrap addresses without replacing the stored `auto` placeholder.

## Dependencies and Integration Points

Uses Kubo config, repo/fsrepo, `config.ParseBootstrapPeers`, `BootstrapPeers`, `BootstrapPeerStrings`, libp2p peer IDs, and multiaddr parsing. The `configExpandAutoName` option is shared with config commands.

## Risks and Edge Cases

Bootstrap peers are trust anchors, so accidental or malicious mutation changes network discovery. Selective removal is intentionally blocked when `auto` is active and AutoConf is enabled because expanded peers are managed externally. Address validation skips `auto`, so future placeholder strings need explicit handling.

## Test Signals

Command tree coverage verifies the bootstrap command paths. Useful targeted tests would cover `default` normalization, disabled AutoConf rejection, sorted output, selective address removal, `auto` plus `rm --all`, and config persistence failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go -->
