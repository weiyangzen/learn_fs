<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/tarball.mk -->
# sources/distributed-fs/ipfs-kubo/mk/tarball.mk

## Purpose

This fragment configures behavior for source tarball builds and exposes tarball creation targets.

## Important APIs, Types, and Functions

It sets `tarball-is` based on `.tarball`, overrides `git-hash` from that file in tarball mode, defines `GOCC`, and provides `go-ipfs-source.tar.gz` and `kubo-source.tar.gz` targets that depend on `distclean` and run `bin/maketarball.sh`.

## Control Flow, State, and Integration

When `.tarball` exists, other Go build settings use vendor mode and fixed version metadata. Tarball targets produce release archives after cleaning.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go, and `bin/maketarball.sh`. Risks include stale `.tarball` metadata and destructive expectations from `distclean`. Release packaging jobs validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/tarball.mk -->
