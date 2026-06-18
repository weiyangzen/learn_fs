# sources/cloud-native/containerd/api/events/container.proto

## Purpose
This proto defines container event payloads for create, update, and delete events.

## Important APIs, Types, And Functions
Package is `containerd.events`; Go package is `github.com/containerd/containerd/api/events;events`. It imports `google/protobuf/any.proto` and `types/fieldpath.proto`, enables `containerd.types.fieldpath_all`, and defines `ContainerCreate`, nested `Runtime`, `ContainerUpdate`, and `ContainerDelete`.

## Control Flow
There is no runtime control flow in the proto. Generation produces protobuf Go types and fieldpath helpers.

## State And Persistence
The schema is persistent API state. Field numbers and names form the compatibility contract for serialized event messages.

## Dependencies And Integration Points
It integrates with containerd's event bus, generated Go code, Buf breaking checks, and fieldpath-based event filtering.

## Risks
Removing or changing field numbers is API-breaking. Runtime options use `Any`, so consumers need type registration to inspect nested options. `fieldpath_all` exposes fields to generated filtering semantics.

## Test Signals
Buf breaking checks, generated code freshness, and event filtering/serialization tests validate it.
