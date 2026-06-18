# sources/cloud-native/ostree/src/ostree/ot-builtin-find-remotes.c

## Purpose
Implements `ostree find-remotes`, which searches configured, mounted, and optionally LAN-advertised repositories for requested collection-ref pairs and can pull the discovered refs into the current repository.

## Important APIs, Types, And Functions
`ostree_builtin_find_remotes()` is the main entry point. Helpers format timestamps and result mappings (`uint64_secs_to_iso8601()`, `format_ref_to_checksum()`), access private remote URLs (`remote_get_uri()`), track found refs (`add_keys_to_set_if_non_null()`), validate finder selections (`validate_finders_list()`), and bridge async APIs (`get_result_cb()`). The command uses `OstreeRepoFinderConfig`, `OstreeRepoFinderMount`, optional `OstreeRepoFinderAvahi`, `ostree_repo_find_remotes_async()/finish()`, and `ostree_repo_pull_from_remotes_async()/finish()`.

## Control Flow
The command opens a writable repo, requires complete `COLLECTION-ID REF` pairs, rejects `--mirror` without `--pull`, applies fsync/cache-dir options, validates refs, and builds a NULL-terminated `OstreeCollectionRef` array. If `--finders` is supplied, it validates non-empty, non-duplicate names and constructs finder objects in the requested order, starting Avahi when LAN discovery is enabled. It locks the console, creates progress for TTYs, starts asynchronous remote discovery, manually iterates the default main context until completion, prints each result's URI, finder, keyring, priority, summary timestamp, and ref-to-checksum mapping, reports unfound refs, and returns unless `--pull` is set. Pull mode builds options, adds mirror flags if requested, asynchronously pulls from all finder results, waits similarly, and prints success.

## State And Persistence
Discovery is read-only apart from cache-dir usage and progress state. Pull mode writes objects, refs, and metadata to the current repository. `--disable-fsync` weakens write durability for the operation. LAN finder startup touches Avahi state outside the repo.

## Dependencies And Integration Points
The command integrates repo finder plugins, remote private data, collection-ref APIs, pull-from-remotes APIs, Avahi when compiled, mount discovery used by `create-usb`, and console progress. It relies on summary metadata from candidate remotes.

## Risks And Edge Cases
The async API is driven by a manual main-context loop, so callbacks must always complete to avoid hanging. `remote_get_uri()` asserts that remote options contain a URL. `add_keys_to_set_if_non_null()` stores keys owned by result hash tables, so the found set must not outlive results. Avahi failures are downgraded to warnings by removing the finder. `--finders` rejects duplicates, and no results is considered a successful lookup.

## Test Signals
Tests should cover finder list validation, config/mount discovery, Avahi-disabled error handling, no-result output, partial found/unfound refs, pull and mirror-pull behavior, cache-dir/fsync options, malformed collection IDs or refs, and result ordering/format stability.
