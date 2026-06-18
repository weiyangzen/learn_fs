<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/auth_test.go

## Purpose
Tests registry auth-config resolution for official and private indexes, including legacy full-URL keys.

## Important APIs, Types, And Functions
`buildAuthConfigs`, `TestResolveAuthConfigIndexServer`, and `TestResolveAuthConfigFullURL` exercise `resolveAuthConfig`.

## Control Flow
The first test checks that official indexes use `IndexServer` credentials while private indexes do not. The second injects auth entries using `https://`, `http://`, bare host, and `/v1/` forms, verifying they resolve only while present.

## State, Dependencies, And Integration Points
State is an in-memory map of `registry.AuthConfig`. It protects daemon credential lookup compatibility with old Docker config formats.

## Risks And Test Signals
The tests do not cover unknown schemes or username-less token auth, but they strongly cover host normalization and official-index special-casing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth_test.go -->
