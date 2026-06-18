<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/libsubid_tag.sh -->
# sources/cloud-native/containers-storage/hack/libsubid_tag.sh

## Purpose
This build helper detects whether the system can compile and link against libsubid.

## Important APIs, Types, And Functions
It checks `${GO:-go} env GOOS`, creates a temporary directory, compiles a C program including `<shadow/subid.h>` and linking `-l subid`, handles ABI differences around `SUBID_ABI_MAJOR`, and prints `libsubid` on success.

## Control Flow
Non-Linux exits with no output. On Linux it builds the probe program and removes the temporary directory through a trap.

## State And Persistence
It writes only a temporary probe binary under `$PWD/tmp.$RANDOM`, then deletes it.

## Dependencies And Integration Points
Build systems can consume its output as a build tag to enable libsubid-backed code.

## Risks And Test Signals
The temporary path is predictable enough for local build tooling but not hardened. The probe assumes `cc`, headers, and libraries are installed and linkable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/libsubid_tag.sh -->
