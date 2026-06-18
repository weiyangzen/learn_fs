# sources/cloud-native/containerd/api/events/content_fieldpath.pb.go

## Purpose
This generated file implements fieldpath lookup helpers for content event messages.

## Important APIs, Types, And Functions
It defines `Field([]string) (string, bool)` for `ContentCreate` and `ContentDelete`.

## Control Flow
Each method rejects empty paths and switches on the first field segment. Both messages expose `digest` when non-empty. `ContentCreate.size` is commented as unhandled by the generator.

## State And Persistence
No persistent state exists.

## Dependencies And Integration Points
It integrates with event filtering code that matches content events by digest.

## Risks
`size` cannot be used as a fieldpath filter through this generated helper. Empty digest returns false, which is appropriate for normal content events but should be known for tests.

## Test Signals
Fieldpath tests should cover digest matches, empty digest, invalid paths, empty path, and the known lack of `size` support.
