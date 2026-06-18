## sources/distributed-fs/ipfs-kubo/test/sharness/t0042-add-skip.sh

Purpose: tests `ipfs add` path skipping/exclusion behavior.

Important control flow: `test_add_skip` builds directory/file fixtures, runs add commands with skip options, and checks that skipped paths are absent while included paths can still be added and retrieved. It runs both offline/repo and daemon-backed portions through standard daemon helpers.

State and dependencies: creates fixture trees and mutates the test repo/blockstore. Depends on `ipfs add`, `ipfs cat`/listing commands, and comparison helpers.

Risks: path matching semantics are user-visible and can be platform-sensitive for separators or hidden files. Test signal is expected add output and retrieval behavior when skip rules are applied.
