# sources/cloud-native/moby/contrib/apparmor/template.go

## Purpose
Holds the AppArmor profile template used by the contrib generator.

## APIs, Types, And Functions
`dockerProfileTemplate` is a large raw string defining the `/usr/bin/docker` profile, child profiles for helper binaries, mount rules, signal and ptrace rules, capability permissions, network access, and profile transitions.

## Control Flow, State, And Integration
There is no Go control flow in this file. The string becomes the rendered AppArmor profile written by `contrib/apparmor/main.go` and loaded by system AppArmor tooling.

## Risks And Test Signals
Risks include over-permissive rules, denied legitimate Docker operations, outdated helper paths, and rootless/user-namespace path mismatches. Integration is with Linux AppArmor policy enforcement and Docker daemon/container setup behavior.
