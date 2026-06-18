<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json -->
# sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json

## Purpose
CRI pod sandbox config fixture for checkpoint/restore tests.

## Important APIs, Types, And Functions
JSON metadata, DNS, resources, labels, annotations, and Linux namespace/SELinux settings.

## Control Flow
Patched with a log directory by scripts then passed to `crictl runp`.

## State And Persistence
Controls test sandbox creation; no standalone persistence.

## Dependencies And Integration Points
CRI sandbox config schema.

## Risks And Test Signals
SELinux/namespace settings may be host-specific; integration scripts validate. Source size reviewed: 50 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/testdata/sandbox_config.json -->
