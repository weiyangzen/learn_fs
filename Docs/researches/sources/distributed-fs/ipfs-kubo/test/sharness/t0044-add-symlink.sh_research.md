## sources/distributed-fs/ipfs-kubo/test/sharness/t0044-add-symlink.sh

Purpose: validates symlink handling during `ipfs add`.

Important control flow: creates files and symlinks, then `test_add_symlinks` runs add variants and checks resulting links/content. It launches a daemon for the online half and stops it afterward.

State and dependencies: creates filesystem symlinks and stores UnixFS DAGs in the repo. Depends on platform symlink support, `ipfs add`, `ipfs ls`/`cat`, and expected UnixFS symlink encoding.

Risks: symlink behavior can differ on Windows or restricted filesystems; dereference versus preserve semantics must remain clear. Test signal is expected representation and retrieval of symlink entries.
