# sources/distributed-fs/ipfs-kubo/test/cli/fuse/realworld_test.go

Purpose: real POSIX-tool FUSE suite exercising writable MFS mount behavior with commands users actually run.

Important APIs/functions: `TestFUSERealWorld`, local helpers `requireTool`, `workdir`, `runCmd`, `randBytes`, daemon config `Mounts.StoreMtime` and `Mounts.StoreMode`, and shared `mountAll`.

Control flow: one daemon/mount is shared, with isolated subdirectories per subtest. Coverage includes shell redirects, `cat`, `seq`, `wc`, `ls`, `stat`, `cp` in/out and recursive, atomic `mv`, `rm -rf`, symlinks/readlink/find traversal, `dd`, `sha256sum`, tar extract/create, `rsync -a`, `rsync --inplace`, and headless `vim` edits. Many assertions compare both FUSE reads and `ipfs files` daemon views.

State/persistence: MFS writes through the mount, metadata preservation, random multi-chunk payloads, symlinks, archives, external command outputs, and daemon-backed content.

Dependencies/integration: FUSE support plus many external binaries; LC_ALL is forced to C for deterministic command output.

Risks/test signals: very high end-user coverage but environment-heavy. Missing tools fail by design; 1 MiB+ payloads exercise multi-chunk paths.
