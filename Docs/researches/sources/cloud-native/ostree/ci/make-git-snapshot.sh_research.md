# sources/cloud-native/ostree/ci/make-git-snapshot.sh

Purpose: creates an xz-compressed source snapshot tarball from the current git revision, including initialized submodules, using a version derived from git tags.

Important APIs/functions: `git rev-parse --show-toplevel`, `git describe --always --tags --match 'v2???.*'`, `git archive`, `git submodule status`, `tar -A`, and `xz`. Generated names are `libostree-${version}.tar.xz`.

Control flow: derives `TOP`, `GITREV`, version, tar names, initializes submodules if expected README files are absent, archives the top-level tree with a versioned prefix, then appends an archive for each submodule at its recorded revision before renaming the temp tar and compressing it.

State and persistence: may initialize git submodules, writes `${PKG_VER}.tar.tmp`, temporary `submodule.tar` files inside each submodule directory, and final `${PKG_VER}.tar.xz`.

Dependencies and integration: supports RPM/Packit source builds and release workflows that need a complete tarball rather than a partial git archive.

Risks and test signals: risks include parsing `git submodule status` with whitespace-sensitive `read`, writing `submodule.tar` into submodule working trees, tag-pattern version drift, and interrupted temp tar state. Signals are successful `tar -tf` with submodule paths and RPM source build consumption.
