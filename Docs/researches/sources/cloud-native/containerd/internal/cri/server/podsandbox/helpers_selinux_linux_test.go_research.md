# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_selinux_linux_test.go

## Purpose

This Linux test file verifies SELinux option translation and validation logic used when creating sandbox OCI specs.

## Important APIs, Types, and Functions

`TestInitSelinuxOpts` exercises nil options, user, role, type, level, and combinations passed through `initLabelsFromOpt`. `TestCheckSelinuxLevel` validates accepted MLS/MCS level formats and rejects malformed strings.

## Control Flow

The tests call helpers directly and assert success or error expectations for each table entry. They rely on the helper's label assembly and regex validation before SELinux label initialization.

## State and Persistence Behavior

No sandbox state is persisted. Depending on SELinux library behavior, label allocation can occur in process state and should be released by callers in production code.

## Dependencies and Integration Points

The tests target `toLabel`, `initLabelsFromOpt`, and `checkSelinuxLevel`, which feed Linux sandbox spec generation and cleanup.

## Risks and Test Signals

The file protects against accepting invalid SELinux level strings and against dropping user-provided SELinux components. It does not exercise container runtime enforcement.
