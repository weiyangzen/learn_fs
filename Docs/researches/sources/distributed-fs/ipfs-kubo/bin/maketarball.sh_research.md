# sources/distributed-fs/ipfs-kubo/bin/maketarball.sh

## Purpose
This release helper creates a source tarball with vendored Go dependencies and normalized permissions.

## Important APIs, Types, And Functions
It uses `mktemp`, `cp -r`, `go mod vendor`, `git describe`, `chmod -R`, and `tar -czf`, with output defaulting to `go-ipfs-source.tar.gz`.

## Control Flow
The script resolves output to an absolute path, copies the working tree to a temp dir, vendors modules, writes `.tarball` metadata, normalizes permissions, creates a gzipped tar excluding `.git`, then removes the temp dir.

## State And Persistence Behavior
It writes the output tarball and transient temp tree. It does not modify the source checkout.

## Dependencies And Integration Points
It integrates Go modules, Git metadata, and release source distribution packaging.

## Risks And Test Signals
Risks include copying untracked local files into the tarball and no trap cleanup on interruption. Signals are a tarball containing vendored dependencies and `.tarball` metadata.
