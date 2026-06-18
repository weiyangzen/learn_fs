# sources/cloud-native/containerd/api/events/content.proto

## Purpose
This proto defines content store event payloads for create and delete operations.

## Important APIs, Types, And Functions
Package is `containerd.events`; Go package is `github.com/containerd/containerd/api/events;events`. It imports `types/fieldpath.proto`, enables `fieldpath_all`, and defines `ContentCreate` (`digest`, `size`) and `ContentDelete` (`digest`).

## Control Flow
There is no runtime control flow. Buf/protoc generation creates Go protobuf and fieldpath files.

## State And Persistence
The schema is persistent API state for serialized content events.

## Dependencies And Integration Points
It integrates with containerd content service events, generated code, fieldpath filtering, and Buf breaking-change checks.

## Risks
Field number changes are API-breaking. `digest` is a string rather than a strongly typed digest, so validation belongs to event producers/consumers.

## Test Signals
Buf breaking checks, generated-code freshness, content event publish/consume tests, and fieldpath filtering on digest validate it.
