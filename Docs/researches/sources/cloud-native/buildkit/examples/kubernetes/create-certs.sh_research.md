# Research: sources/cloud-native/buildkit/examples/kubernetes/create-certs.sh

## Purpose
Bash helper that generates mkcert TLS material and Kubernetes Secret YAMLs for BuildKit.

## Important APIs, Types, and Functions
Validates SAN args and `mkcert`; writes daemon/client PEM files and uses `kubectl create secret generic --dry-run=client -o yaml`.

## Control Flow
Creates `.certs`, generates server and client certs, copies CA files, deletes CA key material, and renders daemon/client secret manifests.

## State and Persistence
Persists `.certs` PEMs, SAN file, and secret YAMLs; does not apply them.

## Dependencies and Integration Points
Depends on bash, mkcert, kubectl, and filesystem permissions. Secret names match the Kubernetes deployment TLS mounts.

## Risks and Edge Cases
Development CA lifecycle, SAN mismatch, and shell splitting are main risks.

## Test Signals
No automated tests; validate by inspecting YAML and starting TLS BuildKit pods.
