<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/git.mk -->
# sources/distributed-fs/ipfs-kubo/mk/git.mk

## Purpose

This makefile fragment derives Git metadata for builds, including commit description, release tag, and normalized origin.

## Important APIs, Types, and Functions

`git-hash` uses `git describe --always --match=NeVeRmAtCh --dirty` with fallback to `git rev-parse --short HEAD`. `git-tag` is set only for clean HEADs with a `v*` tag. `git-origin` normalizes ssh/https origin URLs into `host/org/repo` and strips `.git` and userinfo.

## Control Flow, State, and Integration

The variables are evaluated by Make shell calls and feed version/user-agent/fork detection logic elsewhere in the build.

## Dependencies, Risks, and Test Signals

Dependencies are Git, sed, grep, and shell behavior. Risks include missing Git metadata in tarballs or containers, dirty tree detection differences, and URL normalization edge cases. Build/version tests and release builds are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/git.mk -->
