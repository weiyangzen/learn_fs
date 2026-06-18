# sources/cloud-native/moby/integration-cli/docker_api_build_test.go

## Purpose
Integration tests for `/build` API behavior around remote contexts, Dockerfile selection, cache invalidation, ONBUILD, copy/add, chown, and scratch builds.

## Important APIs and Types
Contains tests such as `TestBuildAPIDockerFileRemote`, remote tarball/custom Dockerfile tests, git `-f` tests, unnormalized tar path cache tests, ONBUILD cache/copy tests, `TestBuildCopyFromForcePull`, and helper `getImageIDsFromBuild`.

## Control Flow, State, and Persistence
Tests create fake HTTP storage, fake git repositories, tar streams, and registry-backed images, then POST to `/build` with query parameters or tar bodies. They parse build output and inspect images/containers to verify selected Dockerfiles, cache boundaries, remote ADD behavior, ownership, and produced image IDs.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on fakecontext/fakegit/fakestorage, request helpers, registry suite, and Docker build backend. It persists built images and may pull/push through test registries. Risks include legacy builder versus BuildKit differences, network timing, and brittle output parsing. These tests signal build API compatibility.
