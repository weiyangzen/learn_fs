# sources/cloud-native/moby/daemon/graphdriver/copy/copy_test.go

Purpose: Linux tests for the graphdriver directory-copy helper.

Important APIs and control flow: `TestCopy` and `TestCopyWithoutRange` copy a deterministic random buffer through `copyRegular` with fast-copy paths enabled or disabled. `TestCopyDir` recursively populates a source tree with random modes and mtimes, copies it, and walks the source comparing destination type/mode/uid/gid/mtime while asserting copied files are not the same inode when on the same device. `populateSrcDir` builds nested directories and files with varied metadata. `TestCopyHardlink` creates two source hardlinks, runs content copy, and asserts destination hardlink inodes match.

State, dependencies, and risks: tests rely on Linux stat fields, local filesystem mtime precision, and permission to set modes/times. They do not test symlinks, devices, sockets, FIFOs, xattrs, clone/range fallback errors, or Hardlink mode directly. The main signal is preserving core metadata and hardlink topology for VFS and other users of `DirCopy`.
