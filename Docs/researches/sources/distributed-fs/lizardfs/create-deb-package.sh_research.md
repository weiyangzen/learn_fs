# sources/distributed-fs/lizardfs/create-deb-package.sh

## Purpose
This script builds Debian packages from a clean cloned copy of the current source tree.

## Important APIs, Types, and Functions
It sets `LIZARDFS_OFFICIAL_BUILD=NO`, determines output/source/working directories, detects distro release with `lsb_release`, chooses systemd or non-systemd rules, clones sources to `/tmp/lizardfs_deb_working_directory/lizardfs`, copies service files into `debian/`, edits changelog version metadata, and runs `dpkg-buildpackage`.

## Control Flow and State
The script deletes and recreates the working directory, clones the repository, copies RPM service files for Debian packaging, strips `-devel` from the first changelog line, derives a package version, optionally appends `BUILD_DATE`, prepends a vendor test-release changelog entry with the current commit, and builds with either default rules or `debian/rules-nosystemd`. Resulting package files are copied back to the original working directory before cleanup.

## Dependencies and Integration Points
It depends on Git, Debian packaging tools, `lsb_release`, `dpkg-buildpackage`, Debian metadata, RPM service-file sources, and the `debian/rules` scripts. The `version` environment variable is consumed by `dh_gencontrol`.

## Risks and Edge Cases
The working directory is a fixed `/tmp` path and is removed recursively. Distribution matching only disables systemd for Debian 7 and Ubuntu 12/14. Changelog parsing is fragile and assumes the first matching header shape. `set -eux` exposes commands and exits on failures.

## Test Signals
Successful `.deb`, `.dsc`, or related artifacts copied to the output directory are the main signal. Build failure from rules, missing deps, or changelog parsing stops the script.
