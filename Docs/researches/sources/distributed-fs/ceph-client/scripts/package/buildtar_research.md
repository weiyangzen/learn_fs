<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/buildtar -->
# sources/distributed-fs/ceph-client/scripts/package/buildtar

## Purpose

`buildtar` stages a built kernel into a directory suitable for tarball packaging, including modules, core boot artifacts, optional DTBs, and architecture-specific images.

## Important APIs, Types, and Functions

It accepts a temporary directory argument and relies on `ARCH`, `SRCARCH`, `KERNELRELEASE`, `KBUILD_IMAGE`, `objtree`, `srctree`, and `KCONFIG_CONFIG`.

## Control Flow

The script recreates the temp directory, optionally installs DTBs when OF early flattree support and an architecture DTB directory exist, runs `modules_install`, copies `System.map`, `.config`, and `vmlinux`, and then selects the boot image path through an architecture `case`.

## State and Persistence Behavior

It deletes and recreates the staging directory, writing files under `boot/`, `boot/dtbs/<release>`, and the module install tree.

## Dependencies and Integration Points

It depends on Kbuild install targets, module installation, architecture boot image conventions, and tar packaging callers.

## Risks and Edge Cases

The file notes stale-image risk for MIPS and arm64 when the first matching file is copied. Architecture-specific image names vary, and missing `KBUILD_IMAGE` or modules can break packaging. It unconditionally recreates the staging directory.

## Test Signals

Run on common architectures, with and without DTBs/modules, and inspect tar contents. Specifically test MIPS/arm64 stale image scenarios and riscv image suffix handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/buildtar -->
