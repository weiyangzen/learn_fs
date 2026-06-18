## sources/distributed-fs/ipfs-kubo/test/sharness/t0051-object.sh

Purpose: broad legacy `ipfs object` command coverage for get/put/data/links/stat/patch operations.

Important helpers and control flow: `test_patch_create_path` builds nested patch paths; `test_object_cmd` creates objects, validates object data and links, performs puts from JSON/protobuf forms, checks stats, and exercises patch add-link/rm-link/append-data/set-data/create-path behavior. It runs around a daemon lifecycle to cover API-backed operation too.

State and dependencies: writes object fixtures and mutates the repo DAG/blockstore. Depends on legacy dag-pb object encoding, `ipfs object` command output, and comparison helpers.

Risks: `ipfs object` is legacy but compatibility-sensitive; exact JSON/text output can change. Test signal is successful object mutation and exact data/link/stat output.
