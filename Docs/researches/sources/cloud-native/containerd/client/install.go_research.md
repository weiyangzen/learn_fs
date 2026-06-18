# Research: sources/cloud-native/containerd/client/install.go

## Purpose
Installs binaries and optionally libraries from an image into containerd's managed opt directory. It is a client helper for images that package executable components intended for local installation.

## Important APIs, Control Flow, And State
`Client.Install` resolves `InstallConfig`, finds the install path via explicit config or the introspection `opt` plugin export, selects platform-specific `bin`/`lib` layer paths, reads the image manifest for the client platform, streams each layer from the content store, decompresses it, filters tar entries, and applies selected entries into the target directory. On Windows it maps `Files\bin`/`Files\lib`, strips the `Files` prefix, and avoids preserving owner. Persistent state is direct filesystem writes under the opt path; content store reads are closed after each layer.

## Dependencies And Integration
Uses image manifest resolution, content readers, containerd archive apply/filter code, compression detection, OS path handling, and introspection plugin exports. It integrates with the daemon opt service contract documented by managed opt.

## Risks And Test Signals
Risks include path traversal or tar metadata assumptions delegated to archive apply, partial installs when a later layer fails, replace protection races around `os.Lstat`, and platform path differences. Tests should cover explicit path versus opt plugin discovery, replace refusal, lib inclusion, decompression errors, Windows path rewrites, and cleanup/close behavior on errors.
