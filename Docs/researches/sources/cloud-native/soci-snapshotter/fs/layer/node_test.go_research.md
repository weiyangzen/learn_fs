# sources/cloud-native/soci-snapshotter/fs/layer/node_test.go

Purpose: tests the `entryToAttr` block-count conversion used when exposing metadata attributes through FUSE.

Important APIs and flow: `TestEntryToAttr` creates a metadata attr with size `1774757`, calls `node.entryToAttr`, normalizes mtime, and asserts that FUSE `Blocks` is reported in 512-byte physical blocks derived from 4096-byte `blockSize`, not a simple ceiling of size divided by block size. It also validates default mode, block size, size, and link count.

State and persistence: pure in-memory conversion test.

Dependencies and integration: targets go-fuse `fuse.Attr` output and metadata attr mapping. It protects behavior observed by overlay/container consumers that inspect stat information.

Risks and test signals: focused regression signal for one subtle stat field. It does not cover owner mapping, symlink size, xattrs, device numbers, or stable inode generation; those are covered partly by broader layer utility tests.
