# sources/compression/xz/build-aux/license-check.sh

## Purpose
This shell script checks for files lacking clear license information. It is not full REUSE compliance; instead it enforces project-specific SPDX and intentionally untagged file allowlists.

## Important Control Flow
It accepts optional `-v`, sets `LC_ALL=C`, defines regex allowlists for SPDX-tagged, intentionally untagged 0BSD/misc files, and generated tarball files. It gets the file list from `git ls-files` when possible, otherwise from `find`, detects files containing `SPDX-License-Identifier:`, splits 0BSD and non-0BSD tagged files, removes allowlisted untagged files and old public-domain `.po` translations, optionally reports all categories, and exits 1 if any unknown files remain.

## State, Dependencies, and Integration
The script changes to the repository root. Dependencies include POSIX shell tools plus non-POSIX `xargs -0`, `grep`, `sort`, `uniq`, `sed`, and optionally `git`. It is used by `Makefile.am` distribution hooks and `mydist`.

## Risks and Test Signals
This is a release hygiene gate. It can miss semantic license problems in allowlisted files but catches new files without SPDX tags. Tarball mode intentionally ignores generated files, so it relies on a clean extracted tree.
