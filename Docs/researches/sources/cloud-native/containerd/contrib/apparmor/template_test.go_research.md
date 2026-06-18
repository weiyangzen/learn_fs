<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template_test.go -->
# sources/cloud-native/containerd/contrib/apparmor/template_test.go

## Purpose
Tests AppArmor profile-name sanitization.

## Important APIs, Types, And Functions
Defines `TestCleanProfileName`.

## Control Flow
Checks replacement/cleaning cases for profile names.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Go testing and `cleanProfileName`.

## Risks And Test Signals
Narrow but useful guard against unsafe profile names. Source size reviewed: 18 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template_test.go -->
