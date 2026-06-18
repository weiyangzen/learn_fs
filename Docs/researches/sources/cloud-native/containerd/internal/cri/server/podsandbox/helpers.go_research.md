# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers.go

## Purpose

This shared helper file defines constants, type registrations, root directory helpers, OCI spec generation, and metadata extraction used throughout the pod sandbox controller.

## Important APIs, Types, and Functions

Constants include `sandboxesDir`, `MetadataKey`, `UpdatedResourcesKey`, and `unknownExitCode`. `UpdatedResources` carries Linux resource and overhead updates stored as sandbox extensions. `getSandboxRootDir` and `getVolatileSandboxRootDir` map sandbox IDs under CRI root/state directories. `runtimeSpec` runs `oci.GenerateSpec` in the Kubernetes namespace. `getMetadata` extracts and type-checks CRI sandbox metadata from container extensions.

## Control Flow

`init` registers `UpdatedResources` with typeurl. Metadata extraction loads all extensions, requires `SandboxMetadataExtension`, unmarshals it, and verifies the concrete type.

## State and Persistence Behavior

The file defines durable extension keys and derives filesystem paths but does not itself write state. The extension registrations are required for marshaling and unmarshaling persisted sandbox metadata/resources.

## Dependencies and Integration Points

It depends on containerd client/container types, CRI labels, sandbox store metadata, typeurl, and the OCI spec generation package.

## Risks and Test Signals

Missing or malformed metadata extensions break recovery and status. Path helpers assume stable root/state config. Tests cover metadata typeurl round-trip and spec generation paths in adjacent files.
