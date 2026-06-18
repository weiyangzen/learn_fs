# sources/distributed-fs/ceph-client/scripts/dtc/update-dtc-source.sh

Purpose: Maintainer script for importing an upstream dtc snapshot into the Linux tree copy under `scripts/dtc`.

Important APIs/commands: `get_last_dtc_version()` derives the last imported upstream tag from git log. The script builds and checks upstream dtc, copies selected dtc, libfdt, and fdtoverlay files, rewrites libfdt includes from angle brackets to quoted local includes, stages files, and creates an editable signed-off git commit.

Control flow: Starts in the Linux tree, computes sibling `../dtc` and local `scripts/dtc` paths, captures the previous import, runs `make clean` and `make check` in upstream, copies manifest files into the kernel copy, applies `sed` include fixups, assembles a commit message with `git describe` and upstream log, and invokes `git commit -e -v -s`.

State/persistence: Mutates the working tree and git index, then creates a commit. It relies on current directory and adjacent upstream checkout layout.

Dependencies/integration: Uses git, make, cp, sed, and shell. It integrates Linux's vendored dtc copy with upstream dtc/libfdt.

Risks: `set -e` stops on command failures, but comments note upstream `make check` historically may not fail for test failures. Paths are unquoted and assume no spaces. It does not build/test the copied kernel-tree dtc. The commit message needs manual editing.

Test signals: Run from a throwaway Linux worktree with an adjacent dtc checkout; verify copied file list, include rewrites, staged paths, commit message range, and failure behavior when upstream build or copy fails.
