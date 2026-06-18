# sources/cloud-native/ostree/src/libostree/ostree-repo-prune.c

Purpose: implements repository garbage collection for loose objects, static deltas, and stale summary cache files, with APIs for standard pruning and pruning from a caller-provided reachable set.

Important APIs/types/functions: public APIs are `ostree_repo_prune_static_deltas`, `ostree_repo_traverse_reachable_refs`, `ostree_repo_prune`, and `ostree_repo_prune_from_reachable`. Internal pieces include `OtPruneData`, `maybe_prune_loose_object`, `_ostree_repo_prune_tmp`, `repo_prune_internal`, and `traverse_reachable_internal`.

Control flow: pruning builds or receives a reachable-object set, lists candidate objects, then visits each serialized object key. Reachable objects update counters; unreachable objects have storage size queried, commit partial markers cleared when applicable, payload-link targets checked against `payload_link_threshold`, and the object deleted unless `NO_PRUNE` is set. Static deltas targeting missing commits are removed, and summary-cache entries for removed remotes are unlinked. Standard `ostree_repo_prune` either traverses all commit objects or only refs depending on flags and depth.

State and persistence: deletes loose objects, static delta directories, and stale summary cache files under repo/cache dirs. It updates output counters for total/pruned objects and bytes. It uses exclusive repo locks for pruning and static-delta deletion; reachable traversal uses shared locks.

Dependencies/integration: depends on object listing/traversal APIs, loose object path helpers, payload-link constants, repo object deletion, storage-size queries, static delta listing/path helpers, refs and collection refs enumeration, and repo lock helpers.

Risks: pruning is destructive unless `OSTREE_REPO_PRUNE_FLAGS_NO_PRUNE` is set. Reachability correctness is critical; wrong refs/depth/flags can delete history or content. Payload-link handling must not remove useful links for large target payloads. Commit-only mode keeps non-commit objects but still reports logs differently. Static delta pruning runs after object traversal and can remove deltas independently of object counts.

Test signals: prune behavior is typically covered by repository and pull tests that create unreachable objects/deltas. Strong tests should assert `NO_PRUNE`, refs-only depth, commit-only behavior, static delta deletion, stale summary cache cleanup, and payload-link threshold behavior.
