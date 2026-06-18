<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/codecov.yml -->
# sources/cloud-native/containerd/codecov.yml

## Purpose
Disables Codecov pull-request comments.

## Important APIs, Types, And Functions
Single YAML key `comment: false`.

## Control Flow
Codecov reads this repository config during coverage processing.

## State And Persistence
No runtime state; affects external coverage service behavior.

## Dependencies And Integration Points
Codecov configuration schema.

## Risks And Test Signals
Minimal; loss of PR coverage comments may hide coverage feedback elsewhere. Validation is Codecov-side. Source size reviewed: 1 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/codecov.yml -->
