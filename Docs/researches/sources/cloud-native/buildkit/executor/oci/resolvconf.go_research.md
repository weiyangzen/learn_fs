# Research: sources/cloud-native/buildkit/executor/oci/resolvconf.go

## Purpose
Resolver configuration generator for containers.

## Important APIs, Types, and Functions
`DNSConfig`, `GetResolvConf`, and resolver path helpers.

## Control Flow
Selects host/filtered resolver source by network mode, applies DNS overrides, writes per-executor `resolv.conf`, returns name for bind mount.

## State and Persistence
Temporary resolver files under executor root.

## Dependencies and Integration Points
Depends on BuildKit net modes, resolvconf helpers, `os.Root`, id mapping. Used by both executor backends before OCI spec generation.

## Risks and Edge Cases
Host resolver variants and bad DNS overrides can break builds.

## Test Signals
`resolvconf_test.go` covers generated content.
