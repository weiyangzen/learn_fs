# sources/distributed-fs/lizardfs/create-osx-package.sh

## Purpose
This script builds a macOS `.pkg` installer for LizardFS from a clean cloned source tree.

## Important APIs, Types, and Functions
It computes `lizard_version` by grepping package version fields from `CMakeLists.txt`, clones the source into `/tmp/lizardfs_osx_working_directory/lizardfs`, configures a Release build with tests off and docs on, runs `make`, installs into a staging directory with `DESTDIR`, and calls `pkgbuild`.

## Control Flow and State
The script deletes and recreates the working directory, clones the source, optionally appends Jenkins `BUILD_NUMBER` when `OFFICIAL_RELEASE=false`, builds under `build`, installs under `build-osx`, and packages that root with identifier `com.lizardfs` and the computed version. Result artifacts are copied back to the original directory, then the working directory is removed.

## Dependencies and Integration Points
It depends on Git, CMake, make, macOS `pkgbuild`, docs tooling if docs are enabled, and top-level CMake install rules.

## Risks and Edge Cases
The fixed `/tmp` working path is destructive. Version extraction by grep/awk is brittle. The condition `[[ ${BUILD_NUMBER:-} && ${OFFICIAL_RELEASE:-} == "false" ]]` depends on Bash semantics and CI variables. Docs are forced on, so missing `a2x` may affect manpage generation.

## Test Signals
The resulting `lizardfs-<version>.pkg` copied to the output directory is the success signal. Configure/build/pkgbuild failures terminate due to `set -eux`.
