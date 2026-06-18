# subset-b-009668 Research



Grouped source research for libtirpc RPC/XDR headers and mergerfs build, configuration, branch, and filesystem helper sources. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.



<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h

## Purpose

This libtirpc public header defines the External Data Representation stream ABI used by ONC/RPC callers. It supplies the `XDR` handle, operation vector, primitive serializer prototypes, inline accessors, record/memory/stdio stream constructors, and network object helpers used by generated rpcgen code and hand-written RPC services. The source was read as a complete 378-line file (13372 bytes).

## Important APIs, Types, and Functions

types: `__rpc_xdr`, `xdr_ops`, `for`, `xdr_discrim`, `netobj`, `xdr_op` macros: `_TIRPC_XDR_H`, `BYTES_PER_XDR_UNIT`, `RNDUP`, `XDR_GETLONG`, `xdr_getlong`, `XDR_PUTLONG`, `xdr_putlong`, `XDR_GETINT32`, `XDR_PUTINT32`, `XDR_GETBYTES`, `xdr_getbytes`, `XDR_PUTBYTES`, and 34 more enum values: `xdr_op` (XDR_ENCODE, XDR_DECODE, XDR_FREE)

## Control Flow

Runtime flow is indirect through the `XDR` operation vector. Callers create a stream with memory/stdio/record constructors, serializers dispatch through `x_ops` to get/put bytes and positions, and higher-level XDR procedures compose primitive encoders based on `x_op` (`XDR_ENCODE`, `XDR_DECODE`, or `XDR_FREE`).

## State and Persistence Behavior

The header owns no persistent storage. State lives in caller-allocated RPC/XDR objects or generated service structures and is valid for the lifetime of the stream, request, response, or decoded allocation.

## Dependencies and Integration Points

direct includes: `stdio.h`, `netinet/in.h`, `rpc/types.h`

## Risks and Edge Cases

ABI compatibility is critical: changing `XDR`, `xdr_ops`, primitive prototypes, alignment macros, or inline integer conversion can break generated RPC code and wire compatibility. `XDR_CONTROL` macro shape also risks statement-context surprises.

## Test Signals

Compile consumers that include the header from C and C++; rpcgen/XDR round-trip tests for primitive and generated structures; ABI/layout checks where supported; interoperability tests against RPC clients/servers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h

## Purpose

This rpcgen-generated libtirpc service header describes the legacy DES crypt RPC program. It defines request and response wire structures, XDR routines for the direction/mode/argument/result types, and client/server stubs for procedure `DES_CRYPT` under `CRYPT_PROG` version 1. The source was read as a complete 109-line file (2414 bytes).

## Important APIs, Types, and Functions

types: `desargs`, `desresp`, `svc_req`, `des_dir`, `des_mode` functions: `xdr_des_dir`, `xdr_des_mode`, `xdr_desargs`, `xdr_desresp` macros: `_CRYPT_H_RPCGEN`, `IXDR_GET_INT32`, `IXDR_PUT_INT32`, `IXDR_GET_U_INT32`, `IXDR_PUT_U_INT32`, `CRYPT_PROG`, `CRYPT_VERS`, `DES_CRYPT` enum values: `des_dir` (ENCRYPT_DES, DECRYPT_DES), `des_mode` (CBC_DES, ECB_DES)

## Control Flow

There is no implementation flow here; rpcgen-generated client/server code calls the declared XDR routines and `des_crypt_1` stubs, while the RPC runtime routes procedure number `DES_CRYPT` to the service implementation.

## State and Persistence Behavior

The header owns no persistent storage. State lives in caller-allocated RPC/XDR objects or generated service structures and is valid for the lifetime of the stream, request, response, or decoded allocation.

## Dependencies and Integration Points

direct includes: `rpc/rpc.h`

## Risks and Edge Cases

The service is legacy DES-oriented and generated; hand edits can desynchronize XDR declarations from implementation. Buffer lengths must be validated by the implementation because the header exposes counted variable arrays.

## Test Signals

Compile consumers that include the header from C and C++; rpcgen/XDR round-trip tests for primitive and generated structures; ABI/layout checks where supported; interoperability tests against RPC clients/servers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/un-namespace.h -->
# sources/user-network-fs/libtirpc/tirpc/un-namespace.h

## Purpose

This FreeBSD-derived internal libtirpc header undefines libc and pthread namespace-remapping macros so implementation files can call or prototype real underscored symbols without macro substitution. It is a portability boundary for RPC code sharing libc headers. The source was read as a complete 153-line file (3956 bytes).

## Important APIs, Types, and Functions

types: `sigaction`, `kevent`, `timespec` functions: `_sigaction`, `_kevent`, `_flock` macros: `_UN_NAMESPACE_H_`

## Control Flow

There is no runtime algorithm. Preprocessor flow undefines namespace-remapped names before later includes/prototypes are processed, guarded by optional header macros such as `_SIGNAL_H_` and `_SYS_EVENT_H_`.

## State and Persistence Behavior

The header owns no persistent storage. State lives in caller-allocated RPC/XDR objects or generated service structures and is valid for the lifetime of the stream, request, response, or decoded allocation.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Incorrect undef coverage can silently call macro-wrapped symbols or hide needed prototypes on some libc/header combinations. The header is portability-sensitive and order-dependent.

## Test Signals

Compile consumers that include the header from C and C++; rpcgen/XDR round-trip tests for primitive and generated structures; ABI/layout checks where supported; interoperability tests against RPC clients/servers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/un-namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/macfuse/.github/FUNDING.yml -->
# sources/user-network-fs/macfuse/.github/FUNDING.yml

## Purpose

This GitHub metadata file declares project sponsorship channels for macFUSE. It is consumed by GitHub rather than the build and has no runtime code, but it affects project funding links shown in repository UI. The source was read as a complete 1-line file (16 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

No executable control flow. GitHub reads the YAML metadata and renders sponsor links.

## State and Persistence Behavior

State is repository metadata persisted as YAML; consumers read it from the checkout or GitHub/docs tooling. There is no runtime mutable state.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risk is limited to stale or malformed sponsorship metadata; it does not affect builds or runtime behavior.

## Test Signals

YAML syntax validation and repository metadata smoke checks are sufficient.

<!-- END_FILE_RESEARCH: sources/user-network-fs/macfuse/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/.github/FUNDING.yml -->
# sources/user-network-fs/mergerfs/.github/FUNDING.yml

## Purpose

This GitHub metadata file declares project sponsorship channels for mergerfs. It is consumed by GitHub rather than the build and has no runtime code, but it affects project funding links shown in repository UI. The source was read as a complete 2-line file (67 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

No executable control flow. GitHub reads the YAML metadata and renders sponsor links.

## State and Persistence Behavior

State is repository metadata persisted as YAML; consumers read it from the checkout or GitHub/docs tooling. There is no runtime mutable state.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risk is limited to stale or malformed sponsorship metadata; it does not affect builds or runtime behavior.

## Test Signals

YAML syntax validation and repository metadata smoke checks are sufficient.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/Makefile -->
# sources/user-network-fs/mergerfs/Makefile

## Purpose

This is the top-level mergerfs build, package, install, and release makefile. It compiles all `src/*.cpp` into `build/mergerfs`, links companion tool symlinks, drives tests, builds vendored libfuse, installs binaries/manpages/preload library, generates changelogs/version headers, and delegates Debian/RPM/container release builds. The source was read as a complete 409-line file (11045 bytes).

## Important APIs, Types, and Functions

make targets: `BUILDDIR`, `DEFAULT_TARGET`, `OPT_FLAGS`, `STATIC_FLAGS`, `LTO_FLAGS`, `SRC`, `OBJS`, `DEPS`, `TESTS`, `TESTS_OBJS`, `TESTS_DEPS`, `MANPAGE`, `override INC_FLAGS`, `override MFS_FLAGS`, `override TESTS_FLAGS`, `LIBFUSE`, `LDLIBS`, `.PHONY`, and 41 more

## Control Flow

Make control flow starts at `all`, builds vendored libfuse, compiles dependency-tracked objects into `build/.objs`, links `mergerfs`, creates symlink tools, and branches into install, package, tarball, release, and container targets. Release targets call `buildtools/build-release` with target-specific arguments.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `fakeroot`, `git`, `rpmbuild`, `make`, `mount`, `dpkg-buildpackage`

## Risks and Edge Cases

Release and install targets mutate the working tree (`VERSION`, `src/version.hpp`, changelogs), shell out to distro packaging tools, and run clean/distclean. Quoting and environment overrides must be preserved for packaging reproducibility.

## Test Signals

`make all`, `make tests`, `make install DESTDIR=...`, `make deb`, `make rpm` on supported distros, and release-target dry runs with a temporary package directory.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-containerimage -->
# sources/user-network-fs/mergerfs/buildtools/build-containerimage

## Purpose

This shell script builds a runnable mergerfs container image from the local checkout with podman. It mounts the checkout read-only, passes a git branch build argument, uses `buildtools/containerimage/Containerfile`, and tags the image as `ghcr.io/trapexit/mergerfs:<branch>`. The source was read as a complete 16-line file (344 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `podman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-containerimage -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-mergerfs -->
# sources/user-network-fs/mergerfs/buildtools/build-mergerfs

## Purpose

This container-side shell script clones a requested mergerfs branch/repository into `/tmp/build`, selects a package build path based on the distribution package manager, and copies produced `.deb`, `.rpm`, or tarball artifacts into `/build`. The source was read as a complete 76-line file (1470 bytes).

## Important APIs, Types, and Functions

shell functions: `rpmbuild_flags`

## Control Flow

The script runs top-level shell logic and helper functions (`rpmbuild_flags`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`, `apt-get`, `make`, `dnf`, `yum`, `apk`, `pkg`, `pacman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-mergerfs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-release -->
# sources/user-network-fs/mergerfs/buildtools/build-release

## Purpose

This Python release orchestrator runs podman builds for one or more generated containerfiles. It can install qemu/binfmt support, prune podman state between builds, bind a local or remote git repo into builds, export packages into a package directory, and append per-containerfile results to `build-report.txt`. The source was read as a complete 178-line file (6099 bytes).

## Important APIs, Types, and Functions

Python functions: `build`, `setup`, `setup_binfmt`, `podman_cleanup`, `parse_args`, `should_skip`, `main`

## Control Flow

Control starts in `main()`, parses CLI arguments, optionally runs setup/cleanup, discovers matching containerfiles, then calls build orchestration helpers (`build`, `setup`, `setup_binfmt`, `podman_cleanup`, `parse_args`, `should_skip`, `main`) in sequence.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `python3`, `podman`, `git`, `apt-get`, `sudo`, `pacman`, `systemctl`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-release -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile -->
# sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile

## Purpose

This two-stage container definition builds a static mergerfs install from a git repository/branch on Alpine, archives the install tree, then produces a minimal runtime image with `mergerfs` as entrypoint. The source was read as a complete 19-line file (587 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `apk`, `git`, `make`, `mount`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/create-branches -->
# sources/user-network-fs/mergerfs/buildtools/create-branches

## Purpose

This developer helper creates two 1 GiB loopback image files under `/tmp`, formats them as ext4, creates mountpoints, and mounts them for local mergerfs branch testing. The source was read as a complete 14-line file (313 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `truncate`, `mkfs.ext4`, `sudo`, `mount`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/create-branches -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/detect-local-target -->
# sources/user-network-fs/mergerfs/buildtools/detect-local-target

## Purpose

This bash helper maps the local architecture and `/etc/os-release` distribution/version into a `buildtools/containerfiles` target name such as `debian:13.amd64`, including derivative and short-version fallbacks. The source was read as a complete 119-line file (3112 bytes).

## Important APIs, Types, and Functions

shell functions: `detect_arch`, `detect_distro`, `find_containerfile`, `main`

## Control Flow

The script runs top-level shell logic and helper functions (`detect_arch`, `detect_distro`, `find_containerfile`, `main`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/detect-local-target -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/gen-containerfiles -->
# sources/user-network-fs/mergerfs/buildtools/gen-containerfiles

## Purpose

This shell generator reads image/platform lines and writes build containerfiles that install build packages, clone/build mergerfs, and export resulting packages from a scratch stage. The source was read as a complete 27-line file (611 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/gen-containerfiles -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/git2debcl -->
# sources/user-network-fs/mergerfs/buildtools/git2debcl

## Purpose

This shell script converts git tag history into Debian changelog entries. It guesses package version/distribution/codename when requested, walks reverse-version-sorted tags, extracts non-merge commits, and formats Debian changelog stanzas. The source was read as a complete 202-line file (5043 bytes).

## Important APIs, Types, and Functions

shell functions: `usage`, `git_tags`, `git_log`, `git_author_and_time`, `git_version`, `guess_distro`, `guess_codename`

## Control Flow

The script runs top-level shell logic and helper functions (`usage`, `git_tags`, `git_log`, `git_author_and_time`, `git_version`, `guess_distro`, `guess_codename`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/git2debcl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-pkgs -->
# sources/user-network-fs/mergerfs/buildtools/install-build-pkgs

## Purpose

This container provisioning script installs distro-specific compiler and packaging dependencies, selects the newest available C++ compiler/toolset where possible, writes `/tmp/build-env`, and verifies C++20 support before package builds proceed. The source was read as a complete 162-line file (3940 bytes).

## Important APIs, Types, and Functions

functions: `main` shell functions: `write_gcc_env`, `write_toolset_env`, `latest_apt_gxx`, `latest_dnf_toolset`, `latest_yum_toolset`, `version_gt`, `check_cxx20`

## Control Flow

The script runs top-level shell logic and helper functions (`write_gcc_env`, `write_toolset_env`, `latest_apt_gxx`, `latest_dnf_toolset`, `latest_yum_toolset`, `version_gt`, `check_cxx20`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `dnf`, `yum`, `apt-get`, `git`, `fakeroot`, `make`, `zypper`, `apk`, `pkg`, `pacman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-pkgs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-tools -->
# sources/user-network-fs/mergerfs/buildtools/install-build-tools

## Purpose

This host setup script installs podman and qemu-user-static tooling for cross-architecture release container builds, using root, sudo, or doas depending on the caller. The source was read as a complete 32-line file (841 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `sudo`, `doas`, `apt-get`, `podman`, `dnf`, `apk`, `python3`, `pacman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-tools -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/update-version -->
# sources/user-network-fs/mergerfs/buildtools/update-version

## Purpose

This script derives the build version from `git describe` or the existing `VERSION` file, writes `VERSION`, and refreshes `src/version.hpp` when the embedded `MERGERFS_VERSION` string changes. The source was read as a complete 20-line file (464 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/update-version -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/debian/rules -->
# sources/user-network-fs/mergerfs/debian/rules

## Purpose

This Debian packaging makefile delegates debhelper targets, overrides auto-build to run `make release`, and overrides auto-install to install mergerfs into the Debian package staging directory with `/usr` as prefix. The source was read as a complete 16-line file (213 bytes).

## Important APIs, Types, and Functions

make targets: `%`, `override_dh_auto_build`, `override_dh_auto_install`

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `make`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/build-venv -->
# sources/user-network-fs/mergerfs/mkdocs/build-venv

## Purpose

This docs helper creates and activates a Python virtualenv, then installs MkDocs, mkdocs-material, pymdown extensions, and mike for versioned documentation publishing. The source was read as a complete 7-line file (149 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `python3`, `pip3`, `mike`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/build-venv -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs -->
# sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs

## Purpose

This docs publishing script uses mike to clear remote docs versions, deploy `master` as `latest`, iterate non-release-candidate tags containing `mkdocs.yml`, deploy each version, set the default version, and restore the original branch. The source was read as a complete 32-line file (789 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`, `mike`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/mkdocs.yml -->
# sources/user-network-fs/mergerfs/mkdocs/mkdocs.yml

## Purpose

This MkDocs configuration defines the mergerfs documentation site, repository/edit links, Material theme features and palettes, markdown extensions, mike versioning, and the full navigation tree for setup, configuration, troubleshooting, FAQ, and support pages. The source was read as a complete 122-line file (3350 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

State is repository metadata persisted as YAML; consumers read it from the checkout or GitHub/docs tooling. There is no runtime mutable state.

## Dependencies and Integration Points

external tools: `mike`, `mount`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/mkdocs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/assert.hpp -->
# sources/user-network-fs/mergerfs/src/assert.hpp

## Purpose

This header defines compile-time and runtime assertion helpers used by mergerfs internals, including `STATIC_ASSERT`, array-length assertions, and optional null-pointer diagnostics before calling `assert`. The source was read as a complete 56-line file (1846 bytes).

## Important APIs, Types, and Functions

types: `StaticAssert` macros: `STATIC_ASSERT`, `STATIC_ARRAYLENGTH_ASSERT`, `ASSERT_NOT_NULL`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `cassert`, `iostream`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/assert.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.cpp -->
# sources/user-network-fs/mergerfs/src/branch.cpp

## Purpose

This file implements or declares a single mergerfs branch record: backing path, access mode, and min-free-space value. Branch records are the units selected by policy code and exposed through the branch configuration string. The source was read as a complete 100-line file (2116 bytes).

## Important APIs, Types, and Functions

functions: `Branch::Branch`, `Branch::to_string`, `Branch::set_minfreespace`, `Branch::minfreespace`, `Branch::ro`, `Branch::nc`, `Branch::ro_or_nc` recognized/config strings include: `branch.hpp`, `num.hpp`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `branch.hpp`, `num.hpp`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.hpp -->
# sources/user-network-fs/mergerfs/src/branch.hpp

## Purpose

This file implements or declares a single mergerfs branch record: backing path, access mode, and min-free-space value. Branch records are the units selected by policy code and exposed through the branch configuration string. The source was read as a complete 67-line file (1526 bytes).

## Important APIs, Types, and Functions

types: `Branch`, `Mode`, `class` functions: `ro`, `nc`, `ro_or_nc`, `to_string`, `minfreespace`, `set_minfreespace` enum values: `Mode` (RO, RW, NC)

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `base_types.h`, `strvec.hpp`, `fs_path.hpp`, `cstdint`, `memory`, `optional`, `string`, `vector`, `variant`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.cpp -->
# sources/user-network-fs/mergerfs/src/branches.cpp

## Purpose

This file implements the thread-safe mutable branch list used by mergerfs. It parses branch expressions, expands globs, canonicalizes paths, preserves per-branch modes/min-free-space, applies add/remove/set operations atomically with shared/unique locks, and detects read-only backing filesystems. The source was read as a complete 564-line file (11604 bytes).

## Important APIs, Types, and Functions

functions: `Branches::Impl::Impl`, `Branches::Impl::minfreespace`, `Branches::Impl::from_string`, `Branches::Impl::to_string`, `Branches::Impl::to_paths`, `Branches::from_string`, `Branches::to_string`, `Branches::find_and_set_mode_ro`, `SrcMounts::SrcMounts`, `SrcMounts::from_string`, `SrcMounts::to_string`, `split`, `parse_mode`, `parse_minfreespace`, and 13 more

## Control Flow

Branch updates clone the current shared implementation, parse the requested operation, mutate the clone, then swap it under a unique lock only if no concurrent writer changed the shared pointer. Readers take shared locks and format or project the current branch vector.

## State and Persistence Behavior

Branch state is copy-on-write through a `shared_ptr` to `Branches::Impl`; each `Branch` stores path, mode, and either explicit min-free-space or a pointer to the collection default. No file-backed persistence is performed here.

## Dependencies and Integration Points

direct includes: `branches.hpp`, `ef.hpp`, `errno.hpp`, `from_string.hpp`, `fs_glob.hpp`, `fs_is_rofs.hpp`, `fs_realpathize.hpp`, `base_types.h`, `num.hpp`, `str.hpp`, `syslog.hpp`, `mutex`, `optional`, `shared_mutex`, and 2 more

## Risks and Edge Cases

Branch parsing is user-facing and concurrency-sensitive. Errors in copy-on-write pointer relinking, glob expansion, min-free-space parsing, or atomic swap retries can expose stale paths, skip valid branches, or race runtime updates.

## Test Signals

Branch expression tests for set/add/remove operations, glob and missing-path behavior, mode/min-free-space parsing, concurrent writer retry behavior, and read-only filesystem detection with mounted fixtures.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.hpp -->
# sources/user-network-fs/mergerfs/src/branches.hpp

## Purpose

This header declares the thread-safe mergerfs branch collection, its internal vector-backed implementation, and `SrcMounts` read-only projection used by the config interface. The source was read as a complete 113-line file (2519 bytes).

## Important APIs, Types, and Functions

types: `Branches`, `Impl`, `SrcMounts` functions: `from_string`, `to_string`, `to_paths`, `find_and_set_mode_ro` macros: `MINFREESPACE_DEFAULT`

## Control Flow

Branch updates clone the current shared implementation, parse the requested operation, mutate the clone, then swap it under a unique lock only if no concurrent writer changed the shared pointer. Readers take shared locks and format or project the current branch vector.

## State and Persistence Behavior

Branch state is copy-on-write through a `shared_ptr` to `Branches::Impl`; each `Branch` stores path, mode, and either explicit min-free-space or a pointer to the collection default. No file-backed persistence is performed here.

## Dependencies and Integration Points

direct includes: `branch.hpp`, `fs_path.hpp`, `strvec.hpp`, `tofrom_string.hpp`, `cstdint`, `memory`, `shared_mutex`, `string`, `vector`

## Risks and Edge Cases

Branch parsing is user-facing and concurrency-sensitive. Errors in copy-on-write pointer relinking, glob expansion, min-free-space parsing, or atomic swap retries can expose stale paths, skip valid branches, or race runtime updates.

## Test Signals

Branch expression tests for set/add/remove operations, glob and missing-path behavior, mode/min-free-space parsing, concurrent writer retry behavior, and read-only filesystem detection with mounted fixtures.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildmap.hpp -->
# sources/user-network-fs/mergerfs/src/buildmap.hpp

## Purpose

This template header provides a small fluent builder wrapper for constructing standard `map` containers and returning a sorted collection at the end of chained insertions. The source was read as a complete 48-line file (1261 bytes).

## Important APIs, Types, and Functions

types: `buildmap`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `algorithm`, `map`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildmap.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildvector.hpp -->
# sources/user-network-fs/mergerfs/src/buildvector.hpp

## Purpose

This template header provides a small fluent builder wrapper for constructing standard `vector` containers and returning a sorted collection at the end of chained insertions. The source was read as a complete 48-line file (1262 bytes).

## Important APIs, Types, and Functions

types: `buildvector` functions: `std::sort`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `algorithm`, `vector`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildvector.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.cpp -->
# sources/user-network-fs/mergerfs/src/caps.cpp

## Purpose

This file sets up Linux process capabilities needed by mergerfs after startup. It manipulates capability sets and securebits/prctl state so the process can retain required filesystem privileges while dropping others. The source was read as a complete 122-line file (2491 bytes).

## Important APIs, Types, and Functions

types: `__user_cap_header_struct`, `__user_cap_data_struct` functions: `caps::setup`, `capset`, `capget`, `return ::syscall`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `caps.hpp`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/prctl.h`, `sys/types.h`, `sys/stat.h`, `sys/syscall.h`, `fcntl.h`, `errno.h`, `string.h`, `grp.h`, `linux/capability.h`, `linux/securebits.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.hpp -->
# sources/user-network-fs/mergerfs/src/caps.hpp

## Purpose

This header exposes the mergerfs capability setup entry point used during process initialization. The source was read as a complete 24-line file (853 bytes).

## Important APIs, Types, and Functions

functions: `setup`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.cpp -->
# sources/user-network-fs/mergerfs/src/category.cpp

## Purpose

This file defines category wrappers for mergerfs policy functions, grouping individual FUSE operations into action/create/search policy categories that can be parsed and rendered through config strings. The source was read as a complete 49-line file (1260 bytes).

## Important APIs, Types, and Functions

functions: `Category::Base::from_string`, `Category::Base::to_string`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `category.hpp`, `errno.hpp`, `str.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.hpp -->
# sources/user-network-fs/mergerfs/src/category.hpp

## Purpose

This file defines category wrappers for mergerfs policy functions, grouping individual FUSE operations into action/create/search policy categories that can be parsed and rendered through config strings. The source was read as a complete 109-line file (2529 bytes).

## Important APIs, Types, and Functions

types: `Base`, `Action`, `Create`, `Search`, `Categories` functions: `from_string`, `to_string`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `funcs.hpp`, `func.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.cpp -->
# sources/user-network-fs/mergerfs/src/config.cpp

## Purpose

This is the runtime configuration registry for mergerfs. It owns the global `cfg`, constructs every mount/config option with defaults, maps user-visible option names to `ToFromString` adapters, parses config files and key-value writes, exposes config xattrs, and enforces read-only options after initialization. The source was read as a complete 525-line file (14775 bytes).

## Important APIs, Types, and Functions

types: `DepthGuard` functions: `Config::CfgConfigFile::CfgConfigFile`, `Config::CfgConfigFile::from_string`, `Config::CfgConfigFile::to_string`, `Config::Config`, `Config::has_key`, `Config::keys_listxattr_size`, `Config::keys_listxattr`, `Config::get`, `Config::set`, `Config::from_stream`, `Config::from_file`, `Config::finish_initializing`, `Config::is_rootdir`, `Config::is_ctrl_file`, and 5 more

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The global `cfg` persists process-wide mount configuration. Config-file errors accumulate in `errs`; `_initialized` freezes read-only options; config xattr listings are generated from `_map`; nested config includes are bounded by thread-local depth.

## Dependencies and Integration Points

direct includes: `config.hpp`, `errno.hpp`, `fmt/core.h`, `fs_path.hpp`, `nonstd/string.hpp`, `str.hpp`, `version.hpp`, `fstream`, `string`, `string.h`

## Risks and Edge Cases

Wrong defaults or map entries can change mount semantics globally. Read-only enforcement must remain correct after initialization, config-file recursion must stay bounded, and xattr list sizing must match the bytes actually written.

## Test Signals

Unit tests for defaults, key aliases, unknown/read-only options, config-file parsing errors, recursion depth, xattr list sizing/content, and runtime set/get round trips.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.hpp -->
# sources/user-network-fs/mergerfs/src/config.hpp

## Purpose

This mergerfs source file is part of the support layer around configuration, filesystem operations, or FUSE integration. The source was read as a complete 224-line file (6279 bytes).

## Important APIs, Types, and Functions

types: `Config`, `CfgConfigFile`, `Err` functions: `to_string`, `from_string`, `finish_initializing`, `has_key`, `keys_listxattr`, `keys_listxattr_size`, `get`, `set`, `from_stream`, `from_file`, `is_rootdir`, `is_ctrl_file`, `is_mergerfs_xattr`, `is_cmd_xattr`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The global `cfg` persists process-wide mount configuration. Config-file errors accumulate in `errs`; `_initialized` freezes read-only options; config xattr listings are generated from `_map`; nested config includes are bounded by thread-local depth.

## Dependencies and Integration Points

direct includes: `branches.hpp`, `category.hpp`, `config_cachefiles.hpp`, `config_debug.hpp`, `config_dummy.hpp`, `config_flushonclose.hpp`, `config_follow_symlinks.hpp`, `config_inodecalc.hpp`, `config_link_exdev.hpp`, `config_log_file.hpp`, `config_moveonenospc.hpp`, `config_nfsopenhack.hpp`, `config_noforget.hpp`, `config_pagesize.hpp`, and 25 more

## Risks and Edge Cases

Wrong defaults or map entries can change mount semantics globally. Read-only enforcement must remain correct after initialization, config-file recursion must stay bounded, and xattr list sizing must match the bytes actually written.

## Test Signals

Unit tests for defaults, key aliases, unknown/read-only options, config-file parsing errors, recursion depth, xattr list sizing/content, and runtime set/get round trips.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.cpp -->
# sources/user-network-fs/mergerfs/src/config_cachefiles.cpp

## Purpose

This implementation parses and formats the mergerfs config option for cache file behavior: `off`, `partial`, `full`, `auto-full`, and `per-process`. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 62-line file (1695 bytes).

## Important APIs, Types, and Functions

functions: `CacheFiles::to_string`, `CacheFiles::from_string` recognized/config strings include: `config_cachefiles.hpp`, `ef.hpp`, `errno.hpp`, `off`, `partial`, `full`, `auto-full`, `per-process`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_cachefiles.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.hpp -->
# sources/user-network-fs/mergerfs/src/config_cachefiles.hpp

## Purpose

This header defines the mergerfs config adapter for cache file behavior: `off`, `partial`, `full`, `auto-full`, and `per-process`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 33-line file (980 bytes).

## Important APIs, Types, and Functions

types: `CacheFilesEnum`, `class` enum values: `CacheFilesEnum` (OFF, PARTIAL, FULL, AUTO_FULL, PER_PROCESS) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_debug.cpp -->
# sources/user-network-fs/mergerfs/src/config_debug.cpp

## Purpose

This implementation parses and formats the mergerfs config option for debug mode and debug output destination integration with libfuse debug logging. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 63-line file (1565 bytes).

## Important APIs, Types, and Functions

functions: `Debug::Debug`, `Debug::to_string`, `Debug::from_string` recognized/config strings include: `config_debug.hpp`, `debug.hpp`, `from_string.hpp`, `fuse_cfg.hpp`, `to_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_debug.hpp`, `debug.hpp`, `from_string.hpp`, `fuse_cfg.hpp`, `to_string.hpp`, `memory`, `string`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_debug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_debug.hpp -->
# sources/user-network-fs/mergerfs/src/config_debug.hpp

## Purpose

This header defines the mergerfs config adapter for debug mode and debug output destination integration with libfuse debug logging. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 31-line file (1017 bytes).

## Important APIs, Types, and Functions

types: `Debug` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_debug.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_dummy.hpp -->
# sources/user-network-fs/mergerfs/src/config_dummy.hpp

## Purpose

This header defines the mergerfs config adapter for hidden compatibility sink for deprecated or no-op options. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 42-line file (1066 bytes).

## Important APIs, Types, and Functions

types: `CfgDummy` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_dummy.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_flushonclose.cpp -->
# sources/user-network-fs/mergerfs/src/config_flushonclose.cpp

## Purpose

This implementation parses and formats the mergerfs config option for flush-on-close policy: `never`, `opened-for-write`, or `always`. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 54-line file (1492 bytes).

## Important APIs, Types, and Functions

functions: `FlushOnClose::to_string`, `FlushOnClose::from_string` recognized/config strings include: `config_flushonclose.hpp`, `ef.hpp`, `errno.hpp`, `never`, `opened-for-write`, `always`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_flushonclose.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_flushonclose.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_flushonclose.hpp -->
# sources/user-network-fs/mergerfs/src/config_flushonclose.hpp

## Purpose

This header defines the mergerfs config adapter for flush-on-close policy: `never`, `opened-for-write`, or `always`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 31-line file (967 bytes).

## Important APIs, Types, and Functions

types: `FlushOnCloseEnum`, `class` enum values: `FlushOnCloseEnum` (NEVER, OPENED_FOR_WRITE, ALWAYS) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_flushonclose.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_follow_symlinks.cpp -->
# sources/user-network-fs/mergerfs/src/config_follow_symlinks.cpp

## Purpose

This implementation parses and formats the mergerfs config option for symlink-following policy: `never`, `directory`, `regular`, or `all`. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 58-line file (1611 bytes).

## Important APIs, Types, and Functions

functions: `FollowSymlinks::to_string`, `FollowSymlinks::from_string` recognized/config strings include: `config_follow_symlinks.hpp`, `ef.hpp`, `errno.hpp`, `never`, `directory`, `regular`, `all`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_follow_symlinks.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_follow_symlinks.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_follow_symlinks.hpp -->
# sources/user-network-fs/mergerfs/src/config_follow_symlinks.hpp

## Purpose

This header defines the mergerfs config adapter for symlink-following policy: `never`, `directory`, `regular`, or `all`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 30-line file (974 bytes).

## Important APIs, Types, and Functions

types: `FollowSymlinksEnum`, `class` enum values: `FollowSymlinksEnum` (NEVER, DIRECTORY, REGULAR, ALL) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_follow_symlinks.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_inodecalc.cpp -->
# sources/user-network-fs/mergerfs/src/config_inodecalc.cpp

## Purpose

This implementation parses and formats the mergerfs config option for inode calculation algorithm delegated to `fs::inode`. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 38-line file (1125 bytes).

## Important APIs, Types, and Functions

functions: `InodeCalc::InodeCalc`, `InodeCalc::to_string`, `InodeCalc::from_string`, `fs::inode::set_algo` recognized/config strings include: `config_inodecalc.hpp`, `fs_inode.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_inodecalc.hpp`, `fs_inode.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_inodecalc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_inodecalc.hpp -->
# sources/user-network-fs/mergerfs/src/config_inodecalc.hpp

## Purpose

This header defines the mergerfs config adapter for inode calculation algorithm delegated to `fs::inode`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 32-line file (1035 bytes).

## Important APIs, Types, and Functions

types: `InodeCalc` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_inodecalc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_link_exdev.cpp -->
# sources/user-network-fs/mergerfs/src/config_link_exdev.cpp

## Purpose

This implementation parses and formats the mergerfs config option for cross-device hard-link behavior: passthrough or relative/absolute symlink strategies. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 58-line file (1676 bytes).

## Important APIs, Types, and Functions

functions: `LinkEXDEV::to_string`, `LinkEXDEV::from_string` recognized/config strings include: `config_link_exdev.hpp`, `ef.hpp`, `errno.hpp`, `passthrough`, `rel-symlink`, `abs-base-symlink`, `abs-pool-symlink`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_link_exdev.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_link_exdev.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_link_exdev.hpp -->
# sources/user-network-fs/mergerfs/src/config_link_exdev.hpp

## Purpose

This header defines the mergerfs config adapter for cross-device hard-link behavior: passthrough or relative/absolute symlink strategies. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 30-line file (989 bytes).

## Important APIs, Types, and Functions

types: `LinkEXDEVEnum`, `class` enum values: `LinkEXDEVEnum` (PASSTHROUGH, REL_SYMLINK, ABS_BASE_SYMLINK, ABS_POOL_SYMLINK) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_link_exdev.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_log_file.cpp -->
# sources/user-network-fs/mergerfs/src/config_log_file.cpp

## Purpose

This implementation parses and formats the mergerfs config option for runtime selection of the debug log output file. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 47-line file (1262 bytes).

## Important APIs, Types, and Functions

functions: `LogFile::LogFile`, `LogFile::to_string`, `LogFile::from_string` recognized/config strings include: `config_log_file.hpp`, `debug.hpp`, `fuse_cfg.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_log_file.hpp`, `debug.hpp`, `fuse_cfg.hpp`, `memory`, `string`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_log_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_log_file.hpp -->
# sources/user-network-fs/mergerfs/src/config_log_file.hpp

## Purpose

This header defines the mergerfs config adapter for runtime selection of the debug log output file. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 31-line file (1030 bytes).

## Important APIs, Types, and Functions

types: `LogFile` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_log_file.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.cpp -->
# sources/user-network-fs/mergerfs/src/config_moveonenospc.cpp

## Purpose

This implementation parses and formats the mergerfs config option for move-on-ENOSPC handling, either false or a create policy such as the default pfrd policy. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 58-line file (1464 bytes).

## Important APIs, Types, and Functions

functions: `MoveOnENOSPC::from_string`, `MoveOnENOSPC::to_string` recognized/config strings include: `config_moveonenospc.hpp`, `ef.hpp`, `errno.hpp`, `from_string.hpp`, `pfrd`, `false`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_moveonenospc.hpp`, `ef.hpp`, `errno.hpp`, `from_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp -->
# sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp

## Purpose

This header defines the mergerfs config adapter for move-on-ENOSPC handling, either false or a create policy such as the default pfrd policy. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 44-line file (1224 bytes).

## Important APIs, Types, and Functions

types: `MoveOnENOSPC` functions: `from_string`, `to_string` recognized/config strings include: `policy.hpp`, `policies.hpp`, `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `policy.hpp`, `policies.hpp`, `tofrom_string.hpp`, `string`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_nfsopenhack.cpp -->
# sources/user-network-fs/mergerfs/src/config_nfsopenhack.cpp

## Purpose

This implementation parses and formats the mergerfs config option for NFS open hack behavior used for compatibility with NFS clients. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 55-line file (1427 bytes).

## Important APIs, Types, and Functions

functions: `NFSOpenHack::from_string`, `NFSOpenHack::to_string` recognized/config strings include: `config_nfsopenhack.hpp`, `ef.hpp`, `errno.hpp`, `off`, `git`, `all`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_nfsopenhack.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_nfsopenhack.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_nfsopenhack.hpp -->
# sources/user-network-fs/mergerfs/src/config_nfsopenhack.hpp

## Purpose

This header defines the mergerfs config adapter for NFS open hack behavior used for compatibility with NFS clients. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 31-line file (946 bytes).

## Important APIs, Types, and Functions

types: `NFSOpenHackEnum`, `class` enum values: `NFSOpenHackEnum` (OFF, GIT, ALL) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_nfsopenhack.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_noforget.hpp -->
# sources/user-network-fs/mergerfs/src/config_noforget.hpp

## Purpose

This header defines the mergerfs config adapter for compatibility adapter that maps noforget/remember aliases onto `fuse_cfg.remember_nodes`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 64-line file (1449 bytes).

## Important APIs, Types, and Functions

types: `CfgNoforget` functions: `from_string`, `to_string` recognized/config strings include: `tofrom_string.hpp`, `from_string.hpp`, `fuse_cfg.hpp`, `true`, `false`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `from_string.hpp`, `fuse_cfg.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_noforget.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pagesize.cpp -->
# sources/user-network-fs/mergerfs/src/config_pagesize.cpp

## Purpose

This implementation parses and formats the mergerfs config option for human-readable page/message size parsing with units and page-size constraints. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 76-line file (1643 bytes).

## Important APIs, Types, and Functions

functions: `ConfigPageSize::ConfigPageSize`, `ConfigPageSize::to_string`, `ConfigPageSize::from_string`, `fatal::abort` recognized/config strings include: `config_pagesize.hpp`, `fatal.hpp`, `from_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_pagesize.hpp`, `fatal.hpp`, `from_string.hpp`, `cassert`, `climits`, `cctype`, `string`, `unistd.h`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pagesize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pagesize.hpp -->
# sources/user-network-fs/mergerfs/src/config_pagesize.hpp

## Purpose

This header defines the mergerfs config adapter for human-readable page/message size parsing with units and page-size constraints. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 50-line file (1247 bytes).

## Important APIs, Types, and Functions

types: `ConfigPageSize` functions: `to_string`, `from_string` recognized/config strings include: `base_types.h`, `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `base_types.h`, `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pagesize.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_passthrough_io.cpp -->
# sources/user-network-fs/mergerfs/src/config_passthrough_io.cpp

## Purpose

This implementation parses and formats the mergerfs config option for FUSE passthrough-IO mode: off, read-only, write-only, or read/write. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 58-line file (1536 bytes).

## Important APIs, Types, and Functions

functions: `PassthroughIO::to_string`, `PassthroughIO::from_string` recognized/config strings include: `config_passthrough_io.hpp`, `ef.hpp`, `errno.hpp`, `off`, `ro`, `wo`, `rw`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_passthrough_io.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_passthrough_io.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_passthrough_io.hpp -->
# sources/user-network-fs/mergerfs/src/config_passthrough_io.hpp

## Purpose

This header defines the mergerfs config adapter for FUSE passthrough-IO mode: off, read-only, write-only, or read/write. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 32-line file (962 bytes).

## Important APIs, Types, and Functions

types: `PassthroughIOEnum`, `class` enum values: `PassthroughIOEnum` (OFF, RO, WO, RW) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_passthrough_io.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pid.hpp -->
# sources/user-network-fs/mergerfs/src/config_pid.hpp

## Purpose

This header defines the mergerfs config adapter for read-only runtime PID reporting through the config interface. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 42-line file (1136 bytes).

## Important APIs, Types, and Functions

types: `ConfigGetPid` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `fmt/core.h`, `sys/types.h`, `unistd.h`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_pid.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_proxy_ioprio.cpp -->
# sources/user-network-fs/mergerfs/src/config_proxy_ioprio.cpp

## Purpose

This implementation parses and formats the mergerfs config option for proxying of caller I/O priority into mergerfs worker behavior. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 51-line file (1252 bytes).

## Important APIs, Types, and Functions

functions: `ProxyIOPrio::ProxyIOPrio`, `ProxyIOPrio::to_string`, `ProxyIOPrio::from_string`, `ioprio::enable` recognized/config strings include: `config_proxy_ioprio.hpp`, `ioprio.hpp`, `from_string.hpp`, `true`, `false`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_proxy_ioprio.hpp`, `ioprio.hpp`, `from_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_proxy_ioprio.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_proxy_ioprio.hpp -->
# sources/user-network-fs/mergerfs/src/config_proxy_ioprio.hpp

## Purpose

This header defines the mergerfs config adapter for proxying of caller I/O priority into mergerfs worker behavior. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 31-line file (1030 bytes).

## Important APIs, Types, and Functions

types: `ProxyIOPrio` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_proxy_ioprio.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp -->
# sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp

## Purpose

This implementation parses and formats the mergerfs config option for cross-device rename behavior: passthrough or symlink fallback modes. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 54-line file (1519 bytes).

## Important APIs, Types, and Functions

functions: `RenameEXDEV::to_string`, `RenameEXDEV::from_string` recognized/config strings include: `config_rename_exdev.hpp`, `ef.hpp`, `errno.hpp`, `passthrough`, `rel-symlink`, `abs-symlink`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_rename_exdev.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.hpp -->
# sources/user-network-fs/mergerfs/src/config_rename_exdev.hpp

## Purpose

This header defines the mergerfs config adapter for cross-device rename behavior: passthrough or symlink fallback modes. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 29-line file (968 bytes).

## Important APIs, Types, and Functions

types: `RenameEXDEVEnum`, `class` enum values: `RenameEXDEVEnum` (PASSTHROUGH, REL_SYMLINK, ABS_SYMLINK) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_set.cpp -->
# sources/user-network-fs/mergerfs/src/config_set.cpp

## Purpose

This implementation parses and formats the mergerfs config option for pipe-delimited string set parsing for options such as cache process names. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 44-line file (1178 bytes).

## Important APIs, Types, and Functions

functions: `ConfigSet::ConfigSet`, `ConfigSet::to_string`, `ConfigSet::from_string` recognized/config strings include: `config_set.hpp`, `str.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_set.hpp`, `str.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_set.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_set.hpp -->
# sources/user-network-fs/mergerfs/src/config_set.hpp

## Purpose

This header defines the mergerfs config adapter for pipe-delimited string set parsing for options such as cache process names. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 35-line file (1102 bytes).

## Important APIs, Types, and Functions

types: `ConfigSet` functions: `to_string`, `from_string` recognized/config strings include: `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `set`, `string`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_set.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfs.cpp -->
# sources/user-network-fs/mergerfs/src/config_statfs.cpp

## Purpose

This implementation parses and formats the mergerfs config option for statfs aggregation strategy: base or full. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 51-line file (1285 bytes).

## Important APIs, Types, and Functions

functions: `StatFS::to_string`, `StatFS::from_string` recognized/config strings include: `config_statfs.hpp`, `ef.hpp`, `errno.hpp`, `base`, `full`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_statfs.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfs.hpp -->
# sources/user-network-fs/mergerfs/src/config_statfs.hpp

## Purpose

This header defines the mergerfs config adapter for statfs aggregation strategy: base or full. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 30-line file (924 bytes).

## Important APIs, Types, and Functions

types: `StatFSEnum`, `class` enum values: `StatFSEnum` (BASE, FULL) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfsignore.cpp -->
# sources/user-network-fs/mergerfs/src/config_statfsignore.cpp

## Purpose

This implementation parses and formats the mergerfs config option for branch classes ignored by statfs: none, read-only, or no-create. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 55-line file (1424 bytes).

## Important APIs, Types, and Functions

functions: `StatFSIgnore::to_string`, `StatFSIgnore::from_string` recognized/config strings include: `config_statfsignore.hpp`, `ef.hpp`, `errno.hpp`, `none`, `ro`, `nc`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_statfsignore.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfsignore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfsignore.hpp -->
# sources/user-network-fs/mergerfs/src/config_statfsignore.hpp

## Purpose

This header defines the mergerfs config adapter for branch classes ignored by statfs: none, read-only, or no-create. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 30-line file (947 bytes).

## Important APIs, Types, and Functions

types: `StatFSIgnoreEnum`, `class` enum values: `StatFSIgnoreEnum` (NONE, RO, NC) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_statfsignore.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_xattr.cpp -->
# sources/user-network-fs/mergerfs/src/config_xattr.cpp

## Purpose

This implementation parses and formats the mergerfs config option for xattr behavior: passthrough, ENOSYS emulation, or ENOATTR emulation. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 55-line file (1417 bytes).

## Important APIs, Types, and Functions

functions: `XAttr::to_string`, `XAttr::from_string` recognized/config strings include: `config_xattr.hpp`, `ef.hpp`, `errno.hpp`, `passthrough`, `nosys`, `noattr`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_xattr.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_xattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_xattr.hpp -->
# sources/user-network-fs/mergerfs/src/config_xattr.hpp

## Purpose

This header defines the mergerfs config adapter for xattr behavior: passthrough, ENOSYS emulation, or ENOATTR emulation. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 32-line file (996 bytes).

## Important APIs, Types, and Functions

types: `XAttrEnum`, `class` enum values: `XAttrEnum` (PASSTHROUGH, NOSYS, NOATTR) recognized/config strings include: `enum.hpp`, `errno.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_xattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/dirinfo.hpp -->
# sources/user-network-fs/mergerfs/src/dirinfo.hpp

## Purpose

This header defines FUSE file-handle carrier state for mergerfs dirinfo objects, including conversions between typed pointers and integer file handles used by libfuse callbacks. The source was read as a complete 62-line file (1354 bytes).

## Important APIs, Types, and Functions

types: `DirInfo` functions: `DirInfo::to_fh`, `DirInfo::from_fh`, `to_fh`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `assert.hpp`, `fh.hpp`, `base_types.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/dirinfo.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ef.hpp -->
# sources/user-network-fs/mergerfs/src/ef.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 21-line file (843 bytes).

## Important APIs, Types, and Functions

macros: `ef`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ef.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/endian.hpp -->
# sources/user-network-fs/mergerfs/src/endian.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 35-line file (992 bytes).

## Important APIs, Types, and Functions

functions: `is_big`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `base_types.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/endian.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/enum.hpp -->
# sources/user-network-fs/mergerfs/src/enum.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 81-line file (1556 bytes).

## Important APIs, Types, and Functions

types: `Enum` functions: `to_string`, `from_string`, `to_int`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/enum.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/errno.hpp -->
# sources/user-network-fs/mergerfs/src/errno.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 33-line file (1138 bytes).

## Important APIs, Types, and Functions

macros: `ENOATTR`, `ENODATA`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `errno.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/errno.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/error.hpp -->
# sources/user-network-fs/mergerfs/src/error.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 59-line file (1290 bytes).

## Important APIs, Types, and Functions

types: `Err`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `errno.hpp`, `optional`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/error.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fh.hpp -->
# sources/user-network-fs/mergerfs/src/fh.hpp

## Purpose

This header defines FUSE file-handle carrier state for mergerfs fh objects, including conversions between typed pointers and integer file handles used by libfuse callbacks. The source was read as a complete 35-line file (962 bytes).

## Important APIs, Types, and Functions

types: `FH`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fh.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fileinfo.hpp -->
# sources/user-network-fs/mergerfs/src/fileinfo.hpp

## Purpose

This header defines FUSE file-handle carrier state for mergerfs fileinfo objects, including conversions between typed pointers and integer file handles used by libfuse callbacks. The source was read as a complete 131-line file (3362 bytes).

## Important APIs, Types, and Functions

types: `which`, `FileInfo` functions: `FileInfo::to_fh`, `FileInfo::from_fh`, `to_fh`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `assert.hpp`, `branch.hpp`, `fh.hpp`, `fs_path.hpp`, `base_types.h`, `shared_mutex`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fileinfo.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/from_string.cpp -->
# sources/user-network-fs/mergerfs/src/from_string.cpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 217-line file (4330 bytes).

## Important APIs, Types, and Functions

functions: `str::from`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `from_string.hpp`, `ef.hpp`, `errno.hpp`, `charconv`, `stdlib.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/from_string.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/from_string.hpp -->
# sources/user-network-fs/mergerfs/src/from_string.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 37-line file (1256 bytes).

## Important APIs, Types, and Functions

functions: `from`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `base_types.h`, `fs_path.hpp`, `string`, `string_view`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/from_string.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.cpp -->
# sources/user-network-fs/mergerfs/src/fs_acl.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for ACL default-detection helper for directories, based on `system.posix_acl_default` xattrs. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 40-line file (1195 bytes).

## Important APIs, Types, and Functions

functions: `fs::acl::dir_has_defaults`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_acl.hpp`, `fs_lgetxattr.hpp`, `fs_path.hpp`, `filesystem`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.hpp -->
# sources/user-network-fs/mergerfs/src/fs_acl.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for ACL default-detection helper for directories, based on `system.posix_acl_default` xattrs. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 31-line file (941 bytes).

## Important APIs, Types, and Functions

functions: `dir_has_defaults`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_attr.cpp -->
# sources/user-network-fs/mergerfs/src/fs_attr.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform-selected file attribute implementation for immutable/flag handling. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 25-line file (992 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_attr_linux.icpp`, `fs_attr_unsupported.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_attr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_attr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_attr.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform-selected file attribute implementation for immutable/flag handling. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 38-line file (1139 bytes).

## Important APIs, Types, and Functions

functions: `copy` macros: `FS_ATTR_NONE`, `FS_ATTR_CLEAR_IMMUTABLE`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `string`, `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_attr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_clonepath.cpp -->
# sources/user-network-fs/mergerfs/src/fs_clonepath.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for recursive metadata/data clone helper used when creating matching paths on another branch. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 179-line file (4266 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fs::clonepath`, `_ignorable_error`, `_clonepath2`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_clonepath.hpp`, `errno.h`, `fs_attr.hpp`, `fs_lchown.hpp`, `fs_lstat.hpp`, `fs_lutimens.hpp`, `fs_mkdir.hpp`, `fs_path.hpp`, `fs_xattr.hpp`, `fs_close.hpp`, `fs_fstat.hpp`, `fs_mkdirat.hpp`, `fs_openat.hpp`, `fs_fchown.hpp`, and 3 more

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_clonepath.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_clonepath.hpp -->
# sources/user-network-fs/mergerfs/src/fs_clonepath.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for recursive metadata/data clone helper used when creating matching paths on another branch. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 30-line file (1048 bytes).

## Important APIs, Types, and Functions

functions: `clonepath`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_clonepath.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_close.hpp -->
# sources/user-network-fs/mergerfs/src/fs_close.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `close(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 41-line file (1037 bytes).

## Important APIs, Types, and Functions

functions: `fs::close`, `close`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_close.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_closedir.hpp -->
# sources/user-network-fs/mergerfs/src/fs_closedir.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `closedir(3)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 42-line file (1065 bytes).

## Important APIs, Types, and Functions

functions: `fs::closedir`, `closedir`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `dirent.h`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_closedir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copy_file_range.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copy_file_range.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform-selected wrapper around copy-file-range style in-kernel copying. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 27-line file (1071 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copy_file_range.hpp`, `fs_copy_file_range_linux.icpp`, `fs_copy_file_range_unsupported.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copy_file_range.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copy_file_range.hpp -->
# sources/user-network-fs/mergerfs/src/fs_copy_file_range.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform-selected wrapper around copy-file-range style in-kernel copying. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 36-line file (1189 bytes).

## Important APIs, Types, and Functions

functions: `copy_file_range`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `cstdint`, `stddef.h`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copy_file_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for copy strategy coordinator that tries clone/copy_file_range/read-write paths and advisory calls. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 47-line file (1406 bytes).

## Important APIs, Types, and Functions

functions: `fs::copydata`, `fs::fadvise_willneed`, `fs::fadvise_sequential`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copydata.hpp`, `fs_copydata_copy_file_range.hpp`, `fs_copydata_readwrite.hpp`, `fs_fadvise.hpp`, `fs_ficlone.hpp`, `stddef.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata.hpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for copy strategy coordinator that tries clone/copy_file_range/read-write paths and advisory calls. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 30-line file (954 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for copy loop that uses `copy_file_range` until the source size is copied or an error/short copy occurs. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 72-line file (1880 bytes).

## Important APIs, Types, and Functions

functions: `fs::copydata_copy_file_range`, `return ::_copydata_copy_file_range`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copydata_copy_file_range.hpp`, `errno.hpp`, `fs_copy_file_range.hpp`, `fs_fstat.hpp`, `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.hpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for copy loop that uses `copy_file_range` until the source size is copied or an error/short copy occurs. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 30-line file (1002 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_copy_file_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for fallback buffered copy loop using `pread` and full `pwrite` helpers. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 84-line file (2034 bytes).

## Important APIs, Types, and Functions

functions: `fs::copydata_readwrite`, `return ::_copydata_readwrite` macros: `BUF_SIZE`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copydata_readwrite.hpp`, `errno.hpp`, `fs_pread.hpp`, `fs_pwriten.hpp`, `vector`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.hpp -->
# sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for fallback buffered copy loop using `pread` and full `pwrite` helpers. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 29-line file (983 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copydata_readwrite.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copyfile.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for high-level copy helper that creates a temporary destination, copies data, restores owner/mode/timestamps/attrs, checks source stability, and optionally cleans up on failure. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 185-line file (4733 bytes).

## Important APIs, Types, and Functions

types: `stat`, `sigaction` functions: `fs::copyfile`, `_ignorable_error`, `std::tie`, `fs::fcntl_setlease_rdlck`, `fs::unlink` macros: `O_NOATIME`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copyfile.hpp`, `fs_attr.hpp`, `fs_close.hpp`, `fs_copydata.hpp`, `fs_fchmod.hpp`, `fs_fchown.hpp`, `fs_fcntl.hpp`, `fs_file_unchanged.hpp`, `fs_fstat.hpp`, `fs_futimens.hpp`, `fs_mktemp.hpp`, `fs_open.hpp`, `fs_path.hpp`, `fs_rename.hpp`, and 5 more

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.hpp -->
# sources/user-network-fs/mergerfs/src/fs_copyfile.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for high-level copy helper that creates a temporary destination, copies data, restores owner/mode/timestamps/attrs, checks source stability, and optionally cleans up on failure. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 50-line file (1435 bytes).

## Important APIs, Types, and Functions

types: `CopyFileFlags`, `stat` macros: `FS_COPYFILE_NONE`, `FS_COPYFILE_CLEANUP_FAILURE`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `base_types.h`, `fs_path.hpp`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_cow.cpp -->
# sources/user-network-fs/mergerfs/src/fs_cow.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for copy-on-write link-break helper for hard-linked files. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 78-line file (1892 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fs::cow::is_eligible`, `fs::cow::break_link`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_cow.hpp`, `errno.hpp`, `fs_lstat.hpp`, `fs_copyfile.hpp`, `fcntl.h`, `sys/stat.h`, `sys/types.h`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_cow.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_cow.hpp -->
# sources/user-network-fs/mergerfs/src/fs_cow.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for copy-on-write link-break helper for hard-linked files. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 39-line file (1190 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `is_eligible`, `break_link`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`, `sys/stat.h`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_cow.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_devid.hpp -->
# sources/user-network-fs/mergerfs/src/fs_devid.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for device-id helper for file descriptors/directories. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 53-line file (1186 bytes).

## Important APIs, Types, and Functions

types: `stat`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fstat.hpp`, `fs_dirfd.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_devid.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dirfd.hpp -->
# sources/user-network-fs/mergerfs/src/fs_dirfd.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for wrapper for extracting a file descriptor from `DIR*`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1027 bytes).

## Important APIs, Types, and Functions

functions: `dirfd`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `dirent.h`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dirfd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dup.hpp -->
# sources/user-network-fs/mergerfs/src/fs_dup.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `dup(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 39-line file (1005 bytes).

## Important APIs, Types, and Functions

functions: `dup`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dup.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dup2.hpp -->
# sources/user-network-fs/mergerfs/src/fs_dup2.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `dup2(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1045 bytes).

## Important APIs, Types, and Functions

functions: `dup2`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_dup2.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_eaccess.hpp -->
# sources/user-network-fs/mergerfs/src/fs_eaccess.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for effective-access helper layered on `faccessat`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 52-line file (1308 bytes).

## Important APIs, Types, and Functions

functions: `eaccess`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_faccessat.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_eaccess.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_exists.hpp -->
# sources/user-network-fs/mergerfs/src/fs_exists.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for existence/type probes built around `lstat`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 99-line file (1981 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `exists`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_lstat.hpp`, `fs_path.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_exists.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_faccessat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_faccessat.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `faccessat(2)` with path handling. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 77-line file (1905 bytes).

## Important APIs, Types, and Functions

functions: `faccessat`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`, `to_neg_errno.hpp`, `string`, `fcntl.h`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_faccessat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fadvise.cpp -->
# sources/user-network-fs/mergerfs/src/fs_fadvise.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform-selected file access advice wrapper with local fallback constants. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 78-line file (2053 bytes).

## Important APIs, Types, and Functions

functions: `fadvise_dontneed`, `fadvise_willneed`, `fadvise_sequential` macros: `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, `POSIX_FADV_WILLNEED`, `POSIX_FADV_DONTNEED`, `POSIX_FADV_NOREUSE`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fcntl.h`, `fs_fadvise_posix.icpp`, `fs_fadvise_unsupported.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fadvise.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fadvise.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fadvise.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform-selected file access advice wrapper with local fallback constants. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1252 bytes).

## Important APIs, Types, and Functions

functions: `fadvise_dontneed`, `fadvise_willneed`, `fadvise_sequential`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fadvise.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fallocate.cpp -->
# sources/user-network-fs/mergerfs/src/fs_fallocate.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform-selected allocation/preallocation wrapper. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 29-line file (1075 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fcntl.h`, `fs_fallocate_linux.icpp`, `fs_fallocate_posix.icpp`, `fs_fallocate_osx.icpp`, `fs_fallocate_unsupported.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fallocate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fallocate.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fallocate.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform-selected allocation/preallocation wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 31-line file (982 bytes).

## Important APIs, Types, and Functions

functions: `fallocate`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fcntl.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fallocate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchmod.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fchmod.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for mode-changing helper that can avoid unnecessary chmod work by checking current file mode. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 78-line file (1733 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fchmod`, `fchmod_check_on_error`, `return ::to_neg_errno` macros: `MODE_BITS`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fstat.hpp`, `to_neg_errno.hpp`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchmod.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchmodat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fchmodat.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for path-relative mode-changing helper using `fchmodat`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 79-line file (1943 bytes).

## Important APIs, Types, and Functions

functions: `fchmodat`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fchmodat.hpp`, `fs_path.hpp`, `to_neg_errno.hpp`, `string`, `fcntl.h`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchmodat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchown.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fchown.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for ownership-changing helper that checks existing uid/gid before issuing chown. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 80-line file (1760 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fchown`, `fchown_check_on_error`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `fs_fstat.hpp`, `sys/stat.h`, `sys/types.h`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fchown.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fcntl.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fcntl.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `fcntl(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 77-line file (1604 bytes).

## Important APIs, Types, and Functions

functions: `fcntl`, `fcntl_setlease_rdlck`, `fcntl_setlease_unlck`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `fcntl.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fcntl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fdatasync.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fdatasync.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `fdatasync(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 47-line file (1129 bytes).

## Important APIs, Types, and Functions

functions: `fdatasync`, `return ::to_neg_errno` macros: `_GNU_SOURCE`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fdatasync.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fgetxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fgetxattr.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for file-descriptor xattr getter wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 67-line file (1658 bytes).

## Important APIs, Types, and Functions

functions: `fgetxattr`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `xattr.hpp`, `filesystem`, `string`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fgetxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ficlone.cpp -->
# sources/user-network-fs/mergerfs/src/fs_ficlone.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform-selected reflink/FICLONE wrapper. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 25-line file (1004 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_ficlone_linux.icpp`, `fs_ficlone_unsupported.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ficlone.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ficlone.hpp -->
# sources/user-network-fs/mergerfs/src/fs_ficlone.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform-selected reflink/FICLONE wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 27-line file (899 bytes).

## Important APIs, Types, and Functions

functions: `ficlone`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ficlone.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_size.cpp -->
# sources/user-network-fs/mergerfs/src/fs_file_size.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for descriptor file-size query helper. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 38-line file (1035 bytes).

## Important APIs, Types, and Functions

types: `stat`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_file_size.hpp`, `fs_fstat.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_size.hpp -->
# sources/user-network-fs/mergerfs/src/fs_file_size.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for descriptor file-size query helper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 28-line file (894 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `base_types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_size.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp -->
# sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for post-copy source stability checker comparing stat metadata. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 54-line file (1557 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `file_changed` macros: `FS_FILE_CHANGED`, `FS_FILE_UNCHANGED`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fstat.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findallfiles.cpp -->
# sources/user-network-fs/mergerfs/src/fs_findallfiles.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for search helper returning all candidate full paths that exist for a logical file. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 44-line file (1311 bytes).

## Important APIs, Types, and Functions

functions: `fs::findallfiles`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_findallfiles.hpp`, `fs_exists.hpp`, `fs_path.hpp`, `string`, `vector`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findallfiles.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findallfiles.hpp -->
# sources/user-network-fs/mergerfs/src/fs_findallfiles.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for search helper returning all candidate full paths that exist for a logical file. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 33-line file (1074 bytes).

## Important APIs, Types, and Functions

functions: `findallfiles`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`, `string`, `vector`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findallfiles.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findonfs.cpp -->
# sources/user-network-fs/mergerfs/src/fs_findonfs.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for branch search helper that maps a logical path to the branch containing the same device/inode. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 74-line file (1805 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fs::findonfs`, `_findonfs`, `return ::_findonfs`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_findonfs.hpp`, `branches.hpp`, `errno.hpp`, `fs_fstat.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `string`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findonfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findonfs.hpp -->
# sources/user-network-fs/mergerfs/src/fs_findonfs.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for branch search helper that maps a logical path to the branch containing the same device/inode. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 33-line file (1049 bytes).

## Important APIs, Types, and Functions

functions: `findonfs`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `branches.hpp`, `string`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_findonfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_flistxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_flistxattr.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for file-descriptor list-xattr wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 46-line file (1178 bytes).

## Important APIs, Types, and Functions

functions: `flistxattr`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `xattr.hpp`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_flistxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fsetxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fsetxattr.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for file-descriptor set-xattr wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 66-line file (1667 bytes).

## Important APIs, Types, and Functions

functions: `fsetxattr`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `xattr.hpp`, `string`, `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fsetxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fstat.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `fstat(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 43-line file (1088 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fstat`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `sys/stat.h`, `sys/types.h`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstatat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fstatat.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for path-relative stat wrapper with no-follow variants. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 86-line file (2154 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `fstatat`, `fstatat_nofollow`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_path.hpp`, `to_neg_errno.hpp`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstatat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstatvfs.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fstatvfs.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `fstatvfs(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1062 bytes).

## Important APIs, Types, and Functions

types: `statvfs` functions: `fstatvfs`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `sys/statvfs.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fstatvfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fsync.hpp -->
# sources/user-network-fs/mergerfs/src/fs_fsync.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `fsync(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 39-line file (1009 bytes).

## Important APIs, Types, and Functions

functions: `fsync`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_fsync.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ftruncate.hpp -->
# sources/user-network-fs/mergerfs/src/fs_ftruncate.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for negative-errno wrapper around `ftruncate(2)`. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1056 bytes).

## Important APIs, Types, and Functions

functions: `ftruncate`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `unistd.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ftruncate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimens.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform dispatcher for setting descriptor timestamps. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 52-line file (1429 bytes).

## Important APIs, Types, and Functions

types: `stat`, `timespec` functions: `futimens`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_stat_utils.hpp`, `sys/stat.h`, `fs_futimens_linux.hpp`, `fs_futimens_freebsd_11.hpp`, `fs_futimens_generic.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_freebsd_11.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimens_freebsd_11.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for FreeBSD 11 direct `futimens` wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1074 bytes).

## Important APIs, Types, and Functions

types: `timespec` functions: `futimens`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_freebsd_11.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp

## Purpose

This header provides a generic `futimens` emulation for platforms without a direct descriptor-based implementation. It validates `timespec` flags, translates `UTIME_NOW`/`UTIME_OMIT`, fetches current timestamps when needed, converts to `timeval`, and calls the project `futimesat` wrapper. The source was read as a complete 281-line file (6101 bytes).

## Important APIs, Types, and Functions

types: `timespec`, `timeval`, `stat` functions: `_can_call_lutimes`, `_should_ignore`, `_should_be_set_to_now`, `_timespec_invalid`, `_flags_invalid`, `_any_timespec_is_utime_omit`, `_any_timespec_is_utime_now`, `_set_utime_omit_to_current_value`, `_set_utime_now_to_now`, `_convert_timespec_to_timeval`, `futimens` macros: `UTIME_NOW`, `UTIME_OMIT`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_futimesat.hpp`, `fs_stat_utils.hpp`, `string`, `fcntl.h`, `sys/stat.h`, `sys/time.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_linux.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimens_linux.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for Linux direct `futimens` wrapper. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 40-line file (1074 bytes).

## Important APIs, Types, and Functions

types: `timespec` functions: `futimens`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `sys/stat.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_linux.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimesat.cpp -->
# sources/user-network-fs/mergerfs/src/fs_futimesat.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for platform dispatcher for `futimesat` compatibility implementations. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 25-line file (997 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_futimesat_osx.icpp`, `fs_futimesat_generic.icpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimesat.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimesat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimesat.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for platform dispatcher for `futimesat` compatibility implementations. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 30-line file (995 bytes).

## Important APIs, Types, and Functions

types: `timeval` functions: `futimesat`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `sys/time.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimesat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getdents64.cpp -->
# sources/user-network-fs/mergerfs/src/fs_getdents64.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for Linux `getdents64` syscall wrapper returning negative errno. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 46-line file (1232 bytes).

## Important APIs, Types, and Functions

functions: `getdents64`, `return ::to_neg_errno`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `to_neg_errno.hpp`, `sys/types.h`, `unistd.h`, `sys/syscall.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getdents64.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getdents64.hpp -->
# sources/user-network-fs/mergerfs/src/fs_getdents64.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for Linux `getdents64` syscall wrapper returning negative errno. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 30-line file (969 bytes).

## Important APIs, Types, and Functions

functions: `getdents64`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `sys/types.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getdents64.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getfl.cpp -->
# sources/user-network-fs/mergerfs/src/fs_getfl.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for helper that reads descriptor flags via the project `fcntl` wrapper. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 29-line file (921 bytes).

## Important APIs, Types, and Functions

functions: `getfl`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fcntl.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getfl.cpp -->
