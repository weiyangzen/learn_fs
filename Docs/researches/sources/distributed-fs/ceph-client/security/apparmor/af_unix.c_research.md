# sources/distributed-fs/ceph-client/security/apparmor/af_unix.c

## Purpose
`af_unix.c` implements fine-grained AppArmor mediation for Unix domain sockets. It handles create, bind, listen, accept, socket option, peer, and file-backed socket revalidation paths, bridging between AppArmor network policy and ordinary path/file mediation for filesystem-backed sockets.

## Important APIs and functions
- `aa_unix_create_perm`, `aa_unix_bind_perm`, `aa_unix_listen_perm`, `aa_unix_accept_perm`, `aa_unix_sock_perm`, `aa_unix_opt_perm`, `aa_unix_peer_perm`, and `aa_unix_file_perm` are the LSM-facing entry points.
- `aa_sunaddr` safely reads `unix_sock->addr` with `smp_load_acquire`.
- `match_to_local`, `match_to_sk`, `match_to_cmd`, `match_to_peer`, and `match_label` walk v9 network DFA states through protocol, address, command selector, peer address, and peer label checks.
- `unix_fs_perm` delegates filesystem-backed socket checks to `aa_path_perm` using inode owner/mode conditions.
- `update_sk_ctx` and `update_peer_ctx` update per-socket cached label/peer contexts.

## Control flow
Create/listen/accept/option/bind operations enter through small public wrappers that capture the current label with `begin_current_label_crit_section`, build audit data, and iterate confined profiles. For v9 network policy, abstract or anonymous sockets are matched in the network DFA; filesystem sockets are usually checked as paths. If v9 is not mediated, the code falls back to older address-family socket mediation via `aa_profile_af_perm` or `aa_profile_af_sk_perm`.

Peer operations are stricter. `aa_unix_peer_perm` requires both socket locks to be held and compares the local socket, peer address/path, and peer label. `aa_unix_file_perm` revalidates open Unix socket files when peer labels or cached labels changed; for non-filesystem sockets it cross-checks both directions with `xcheck`, then updates peer caches after success.

## State and persistence
The file updates per-socket `aa_sk_ctx` fields: current socket label, peer label, and `peer_lastupdate`. These are RCU-protected labels mutated under the Unix socket lock. No persistent disk state is written, but successful checks influence later fast-path decisions through cached labels.

## Dependencies and integration
It depends on Unix socket internals, AppArmor labels, path mediation, net mediation, file permission masks, audit helpers, and policy DFA helpers. Filesystem socket handling intentionally integrates with `file.c` and path rules so Unix socket paths are governed like filesystem objects when appropriate.

## Risks
The code is sensitive to socket lifetime, lock ordering, and RCU label access. Address matching uses special in-band bytes for anonymous, abstract, disconnected, and shutdown addresses; policy compiler/runtime mismatches could misclassify endpoints. The comments note incomplete local label matching and implicit delegation for shutdown/deleted filesystem sockets. Cache update races are handled conservatively, but stale peer information can cause extra revalidation.

## Test signals
Exercise abstract, anonymous, autobind, and filesystem Unix sockets across stream and datagram modes. Test bind/listen/accept, peer send/connect checks, socket option mediation, inherited/open socket revalidation after profile replacement, and filesystem socket fallback to path permissions. Audit records should include operation, class, peer label or path, address failures, and correct allowed/denied outcomes.
