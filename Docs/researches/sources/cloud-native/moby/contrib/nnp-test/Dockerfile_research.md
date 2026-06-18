# sources/cloud-native/moby/contrib/nnp-test/Dockerfile

## Purpose
Builds a small image for testing Linux no-new-privileges behavior.

## APIs, Types, And Functions
The Dockerfile compiles or packages `nnp-test.c` into a container image. Its interface is the resulting test executable image rather than a code API.

## Control Flow, State, And Integration
Build steps create an image containing the no-new-privileges test binary and any minimal runtime dependencies. The produced image is used to verify security-option behavior at container runtime.

## Risks And Test Signals
Risks include compiler/base-image drift and mismatched file capabilities or setuid expectations. Integration is with Docker security option tests around `no-new-privileges`.
