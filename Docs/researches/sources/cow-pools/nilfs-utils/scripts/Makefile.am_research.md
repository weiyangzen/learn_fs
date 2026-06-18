# File Research: sources/cow-pools/nilfs-utils/scripts/Makefile.am

## Purpose
This Automake fragment declares script distribution behavior for the `scripts` directory.

## Contents
The file contains:
```make
dist_noinst_SCRIPTS = checkpatch.pl
```

## Build Meaning
- `checkpatch.pl` is included in distribution tarballs.
- It is not installed by `make install`.
- The script is treated as a developer/maintainer helper rather than runtime user command.

## Dependencies
No local build rules, conditionals, or generated outputs are defined here.
