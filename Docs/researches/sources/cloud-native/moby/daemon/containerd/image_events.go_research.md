# sources/cloud-native/moby/daemon/containerd/image_events.go

## Purpose
Centralizes image event logging for the containerd-backed image service and safely copies image labels into event attributes when available.

## Important APIs, Types, And Functions
- `LogImageEvent(ctx, imageID, refName, action)` logs events with labels from `GetImage` when possible.
- `logImageEvent(img, refName, action)` logs name-only events from a known containerd image.
- `copyAttributes` copies labels into a destination map without aliasing.

## Control Flow
Public logging uses `context.WithoutCancel`, attempts to load image metadata to copy config labels, adds a `name` attribute when a reference name is provided, and logs through daemon events service. The private helper bypasses image lookup and logs digest plus optional name.

## State And Persistence
Writes daemon event records through `eventsService`; does not mutate images. Attribute maps are newly allocated per event.

## Dependencies And Integration Points
Depends on daemon event service, API event types, containerd image records, and image backend get options. Used by create, delete, save, load, untag, and related image operations.

## Risks And Edge Cases
Delete events often occur after image metadata is gone, so label copy is best effort. Event consumers may see different attributes depending on whether metadata was still readable. Labels are copied to avoid mutation by event triggers.

## Test Signals
No direct tests in this subset. Event integration tests should verify action type, actor ID, `name` attribute, and label immutability.
