<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/util.mk -->
# sources/distributed-fs/ipfs-kubo/mk/util.mk

## Purpose

This fragment defines cross-platform Make utility variables.

## Important APIs, Types, and Functions

It detects `OS`, sets `WINDOWS`, executable suffix `?exe`, and `PATH_SEP`. It also notes that build platforms now live in `.github/build-platforms.yml`.

## Control Flow, State, and Integration

The variables are consumed by other Make fragments to build executable names and PATH values portably.

## Dependencies, Risks, and Test Signals

Dependencies are shell `uname` and GNU Make conditionals. Risks include ambiguous `?exe` variable naming and incorrect Windows detection outside native Windows Make. Cross-platform build checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/util.mk -->
