# sources/distributed-fs/ceph-client/tools/docs/find-unused-docs.sh

Purpose: Finds C files under a given directory that contain exported kernel-doc comments but are not included by formatted documentation.

Important APIs, types, and functions: Validates kernel tree root and one directory argument. Builds `FILES_INCLUDED` associative array from `Documentation/**/*.rst` lines containing `.. kernel-doc`. Runs `tools/docs/kernel-doc -export` on candidate C files.

Control flow: From root validation, changes to the docs tool directory then kernel root, collects included files from Documentation, returns to root, finds `*.c` under the requested directory, skips files already included, invokes kernel-doc export, and prints files with non-empty exported documentation.

State and persistence: Read-only. Writes file paths to stdout.

Dependencies and integration points: Requires Bash, grep, find, and `tools/docs/kernel-doc`. Used by documentation coverage audits.

Risks: Uses whitespace splitting for included paths and `for file in \`find ...\``, so paths with spaces break. Only C files are checked. Inclusion detection is simple and may miss kernel-doc directives with unusual formatting.

Test signals: Run on a small directory with known included/unincluded exported kernel-doc comments, invalid cwd, missing argument, and nonexistent directory.
