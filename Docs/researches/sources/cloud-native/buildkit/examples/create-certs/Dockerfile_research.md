# Research: sources/cloud-native/buildkit/examples/create-certs/Dockerfile

## Purpose
Two-stage Dockerfile that generates daemon and client TLS certificate bundles for BuildKit examples using mkcert.

## Important APIs, Types, and Functions
Uses Alpine `gen` stage, `SAN` and `SAN_CLIENT` args, `mkcert`, and a final scratch export of `/certs`.

## Control Flow
Installs mkcert, writes SAN list, creates daemon and client cert/key pairs, copies the root CA to both bundles, removes root CA private material, and copies artifacts into scratch.

## State and Persistence
Persists generated PEM files in the build output image; no runtime state.

## Dependencies and Integration Points
Depends on Dockerfile frontend v1, Alpine edge testing, mkcert, and ca-certificates. Feeds Kubernetes and remote TLS BuildKit examples.

## Risks and Edge Cases
`alpine:edge` and testing repo reduce reproducibility; certs are development PKI and SAN quoting matters.

## Test Signals
No direct tests; validation is successful image build and TLS consumers starting correctly.
