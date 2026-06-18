# sources/cloud-native/ostree/man/ostree.repo-config.xml

Purpose: This DocBook refentry documents the OSTree repository `config` keyfile. It is the main user-editable repository configuration contract, covering global `[core]`, per-remote `[remote "name"]`, `[sysroot]`, and experimental `[ex-integrity]` sections.

Important configuration keys: Core keys include `mode`, `repo_version`, `auto-update-summary`, deprecated `commit-update-summary`, `fsync`, `per-object-fsync`, `min-free-space-percent`, `min-free-space-size`, `add-remotes-config-dir`, `payload-link-threshold`, `collection-id`, `locking`, `lock-timeout-secs`, `default-repo-finders`, and `no-deltas-in-summary`. Remote keys include `url`, `contenturl`, `branches`, `proxy`, `gpg-verify`, `gpg-verify-summary`, TLS settings, `http2`, `unconfigured-state`, and `custom-backend`. Sysroot keys include `readonly`, `bootloader`, `boot-counting-tries`, `bls-append-except-default`, and `bootprefix`.

Control flow and state: This file is declarative state consumed by libostree and CLI commands when opening repositories, resolving remotes, pulling objects, checking signatures, updating summaries, locking repositories, and writing bootloader/sysroot state. Remotes may also persist outside the repo in `/etc/ostree/remotes.d/*.conf`.

Dependencies and integration points: Integrates with GLib keyfile parsing, repository open/init code, HTTP/TLS stack, GPG verification, summary generation, static delta indexes, collection-ID peer discovery, Flatpak/libostree multi-process locking, BLS bootloader handling, and OS vendor subscription hooks via `unconfigured-state` or `custom-backend`.

Risks: Several keys affect durability and security. Disabling `fsync` weakens crash safety; `tls-permissive=false` should remain the safe default; `gpg-verify=false` removes commit signature enforcement; `min-free-space-*` semantics exclude metadata objects; and `lock-timeout-secs=300` is called out as flake-prone. Documentation must stay aligned with defaults because these options control production update safety.

Test signals: Config parser tests should exercise precedence between `min-free-space-size` and percent, deprecated alias behavior, remote directory inclusion rules, mirrorlist URL parsing, TLS option propagation, locking timeout behavior, and summary delta-index behavior for `no-deltas-in-summary`.
