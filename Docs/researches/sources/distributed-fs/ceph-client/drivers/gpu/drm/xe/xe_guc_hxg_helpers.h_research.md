# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hxg_helpers.h

## Purpose
Provides small helpers for GuC HXG message sizing, type classification, stringification, and host-side response encoding.

## Important APIs, Types, And Functions
Defines `hxg_sizeof`, `guc_hxg_type_to_string`, `guc_hxg_type_is_action`, `guc_hxg_type_is_reply`, and encoders for success, failure, busy, and retry messages. The encoders fill message dword 0 with host origin, HXG type, and type-specific data fields, returning the encoded message length.

## Control Flow
Callers inspect the type field with the classifier helpers or build a response with one of the inline encoders. `hxg_sizeof` forces compile-time failure if a type is not u32-aligned.

## State And Persistence
No persistent state is owned by this header; it operates on caller-provided message buffers.

## Dependencies And Integration Points
Depends on GuC messages ABI masks and Linux bitfield helpers. Used by relay and other GuC communication paths that exchange HXG messages.

## Risks And Test Signals
The helpers assume the ABI masks match firmware. Message-buffer callers must provide enough space for the returned length. Relay KUnit paths and CT message protocol tests are the main validation signals.
