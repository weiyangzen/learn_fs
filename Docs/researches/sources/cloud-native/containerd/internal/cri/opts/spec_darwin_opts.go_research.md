# sources/cloud-native/containerd/internal/cri/opts/spec_darwin_opts.go

## Purpose

This file adds Darwin-specific mount handling for CRI-generated OCI specs.

## Important APIs, Types, and Functions

`WithDarwinMounts` merges CRI mounts with extra mounts, lets CRI mounts override extras by destination, filters default mounts that are overridden, creates missing host paths, resolves symlinks, and appends bind mounts with `ro` or `rw` options.

## Control Flow

The option copies CRI mounts first, appends non-overridden extras, sorts by destination path depth, builds a destination set, removes default mounts with those destinations, then appends parsed bind mounts to the spec.

## State and Persistence Behavior

It may create host directories for missing mount sources. It mutates only the in-memory OCI spec mounts.

## Dependencies and Integration Points

It depends on CRI runtime mounts, OCI spec options, containerd OS abstraction, and shared `orderedMounts`/`cleanMount`. Darwin spec construction in `container_create.go` uses this option.

## Risks and Edge Cases

Creating missing host paths mirrors Linux behavior but may surprise callers expecting validation-only behavior. Destination comparisons use cleaned paths; named-pipe special handling comes from `cleanMount` in Windows opts, so cross-platform build composition matters.

## Test Signals

Tests should cover CRI overriding extra/default mounts, path sorting, missing source directory creation, symlink resolution errors, and readonly option generation.
