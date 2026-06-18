## sources/distributed-fs/ipfs-kubo/test/sharness/t0080-repo.sh

Purpose: broad integration coverage for repo garbage collection, pin commands, refs traversal, repo stats, and repo version reporting.

Important APIs and helpers: uses `ipfs repo gc`, `ipfs add`, `ipfs pin add/rm/ls`, `ipfs refs`, `ipfs refs local`, `ipfs repo stat`, `ipfs repo version`, `random-data`, `test_cmp`, and helper `get_field_num` for parsing stat values.

Control flow and state: adds files and random multiblock data, observes automatic recursive pins, removes pins, confirms GC removes only unpinned blocks, checks `--silent`, direct vs recursive pin conflicts, indirect pin listing, refs uniqueness and recursion behavior, and repo stats before and after adding data. It also removes `Datastore.StorageMax` from config and ensures stat still works.

Dependencies and integration points: covers blockstore persistence, pinset state, DAG traversal, local refs index, storage accounting, config-backed storage limit display, and repo version metadata.

Risks and test signals: protects against data loss from GC, inaccurate pin classification, duplicate or missing refs, and unstable stat output. Test signals include exact pin output, content retrievability, absence from `refs local` after GC, increasing repo size, expected human-readable stats fields, and version text.
