<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh -->
# sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh

## Purpose

This shell script installs and loads a macOS launchd plist for running the IPFS daemon.

## Important APIs, Types, and Functions

The script derives its source directory, sets `plist=io.ipfs.ipfs-daemon.plist`, chooses `$HOME/Library/LaunchAgents`, defaults `IPFS_PATH` to `$HOME/.ipfs`, resolves `ipfs` binary path with `which`, substitutes `{{IPFS_PATH}}` and `{{IPFS_BIN}}` into the plist via `sed`, unloads an existing job, and loads or bootstraps based on macOS version.

## Control Flow, State, and Integration

It writes the generated plist into the user's LaunchAgents directory and invokes `launchctl`. For newer macOS versions it changes ownership to root and bootstraps into the system domain.

## Dependencies, Risks, and Test Signals

Dependencies are bash, sed, `which`, `launchctl`, `sw_vers`, and sudo for newer systems. Risks include weak quoting around paths, questionable `if [ $? ]` logic that is always true for non-empty status strings, version parsing assumptions, and root ownership of a user LaunchAgents path. Manual macOS install testing is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh -->
