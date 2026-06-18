## sources/distributed-fs/ipfs-kubo/test/sharness/t0043-add-w.sh

Purpose: tests `ipfs add -w` wrapping behavior for files, directories, and path naming.

Important control flow: `test_add_w` prepares fixtures, runs add with wrapping options, captures wrapper/root hashes, and validates listing/cat paths through the wrapper. It includes daemon-backed validation after launching a daemon and then kills it.

State and dependencies: writes fixture files/directories and stores resulting DAGs in the temporary repo. Depends on `ipfs add -w`, `ipfs ls`, `ipfs cat`, and deterministic expected output.

Risks: wrapper DAG layout and path names are compatibility-sensitive. Test signal is that wrapped roots expose expected child names and content under both CLI and daemon contexts.
