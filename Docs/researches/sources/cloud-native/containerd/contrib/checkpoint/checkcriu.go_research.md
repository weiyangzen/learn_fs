<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go -->
# sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go

## Purpose
Small prerequisite checker for CRIU availability used by checkpoint restore scripts.

## Important APIs, Types, And Functions
Defines `main`.

## Control Flow
Attempts to execute/query CRIU support and exits non-zero on failure.

## State And Persistence
No persistence beyond process exit status.

## Dependencies And Integration Points
CRIU installed in PATH and host kernel support.

## Risks And Test Signals
Only checks availability, not full checkpoint success. Used by shell integration scripts. Source size reviewed: 32 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkcriu.go -->
