# sources/cloud-native/moby/daemon/apparmor_linux.go

## Purpose
Detects whether AppArmor is supported and accessible on Linux.

## APIs, Types, And Functions
The file defines `appArmorSupported`, using containerd's AppArmor host support probe and Moby rootless detached-netns detection.

## Control Flow, State, And Integration
The function first rejects detached rootless network namespace mode because AppArmor sysfs is netns-scoped and inaccessible, then delegates to `apparmor.HostSupports`. It reads host/kernel state but does not mutate it.

## Risks And Test Signals
Risks include false negatives in rootless configurations and host probe behavior changes. Integration is with default profile selection and daemon security option setup.
