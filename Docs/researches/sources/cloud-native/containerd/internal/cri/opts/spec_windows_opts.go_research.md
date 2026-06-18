# sources/cloud-native/containerd/internal/cri/opts/spec_windows_opts.go

## Purpose

This file contains Windows-specific OCI spec options for mounts, resources, credential specs, affinity, and device assignment.

## Important APIs, Types, and Functions

`namedPipePath` and `cleanMount` preserve Windows named pipe paths. `parseMount` validates/creates/resolves host paths and normalizes destinations. `WithWindowsMounts` merges CRI/default/extra mounts. `WithWindowsResources` maps CRI CPU, memory, and affinity fields. `WithWindowsDefaultSandboxShares` sets default sandbox CPU shares. `WithWindowsCredentialSpec` sets gMSA credential spec. `WithWindowsDevices` parses CRI device host paths into OCI Windows device IDs.

## Control Flow

Mount handling appends non-overridden extras, sorts by destination depth, removes overridden defaults, parses each mount, and appends it. `parseMount` avoids stat/clean operations for named pipes, creates missing non-pipe host paths, resolves symlinks, cleans paths for hcsshim, prefixes absolute `\...` destinations with `C:`, rejects destination `C:` drive, and sets `ro`/`rw`. Device handling requires empty `ContainerPath` and `Permissions`, supports legacy `class/<id>` by rewriting to `class://<id>`, splits `IDType://ID`, and delegates to OCI Windows device opts.

## State and Persistence Behavior

It may create missing host directories and mutates only in-memory OCI Windows/mount fields. It does not persist credential specs beyond the OCI spec field.

## Dependencies and Integration Points

It depends on containerd OS abstraction, CRI runtime types, OCI runtime specs, and containerd OCI helpers. Windows container spec construction composes these options.

## Risks and Edge Cases

Named pipe paths must not be cleaned or opened because that can break pipe semantics. Destination path normalization must avoid invalid `C:` root mounts. Device format validation is strict and returns errors for Linux-style CRI device fields. CPU shares/maximum are uint16 conversions from CRI values.

## Test Signals

Existing Windows tests cover devices, resources, and drive mounts. Additional checks should cover named pipe mounts, C: destination rejection, absolute destination prefixing, credential specs, and affinity filtering of nil entries.
