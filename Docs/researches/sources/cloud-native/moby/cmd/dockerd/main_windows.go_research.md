# sources/cloud-native/moby/cmd/dockerd/main_windows.go

## Purpose
Pulls Windows resources into the dockerd binary on Windows builds.

## APIs, Types, And Functions
The file contains a blank import of `github.com/moby/moby/v2/cmd/dockerd/winresources`. It has no functions or runtime logic of its own.

## Control Flow, State, And Integration
The blank import ensures the package and its generated resource objects are linked when building Windows dockerd. State is build/link metadata rather than runtime state.

## Risks And Test Signals
Risks are build-time: removing or renaming the import can drop version info, icons, manifests, or event message resources from Windows binaries. Integration is with go-winres and Windows release packaging.
