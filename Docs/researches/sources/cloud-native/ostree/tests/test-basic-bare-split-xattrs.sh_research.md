# sources/cloud-native/ostree/tests/test-basic-bare-split-xattrs.sh

Purpose: tests experimental `bare-split-xattrs` repository mode initialization, fsck, disabled writes, and fixture reading.

Important APIs/functions: `ostree init --mode bare-split-xattrs`, `fsck --all`, `commit --orphan`, environment `OSTREE_EXP_WRITE_BARE_SPLIT_XATTRS=true`, sudo tar extraction, `log`, `ls -X`, symlink and xattr assertions.

Control flow: verifies mode init/config, fsck on empty repo, rejects normal commit, allows experimental commit but expects fsck failure, then if privileged/sudo-capable extracts a fixture tarball and validates commit log, xattr output, and symlink content.

State/persistence: creates/removes `repo`, `files`, and fixture objects. Dependencies include sudo for ownership-preserving fixture extraction.

Integration/risk/test signals: documents and guards an experimental storage mode. Risks include privilege gating and intentionally failing experimental writes. TAP marks fixture read skipped if sudo is unavailable.
