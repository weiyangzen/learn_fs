<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/install.sh -->
# sources/distributed-fs/ceph-client/arch/parisc/install.sh

Source read size: 41 lines, 900 bytes.

Purpose: architecture install helper for `make install` on PA-RISC. Important behavior: accepts kernel version, image file, System.map, and install path; detects compressed `vmlinuz` by basename, rotates existing image and System.map to `.old`, copies/cats the new artifacts, and exits on errors via `set -e`. Control flow: choose base name, rotate old target if present, write image, rotate old map if present, copy map. State and persistence: mutates files under the requested install path. Dependencies and integration points: invoked by kernel build install targets and boot-loader packaging workflows. Risks: unquoted positional parameters make spaces unsafe; `cat >` can leave partial images on interruption; no permission/disk-space preflight. Test signals: run with temporary install directory for compressed and uncompressed image names, existing-file rotation, missing argument failure, and shellcheck-style quoting review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/install.sh -->
