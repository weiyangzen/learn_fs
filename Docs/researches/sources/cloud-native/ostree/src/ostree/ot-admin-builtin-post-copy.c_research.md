<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c

## Purpose
Implements `ostree admin post-copy`, updating repo and deployment metadata after a sysroot copy.

## Important APIs and Types
Exports `ot_admin_builtin_post_copy` and calls `ostree_sysroot_update_post_copy`.

## Control Flow
The command parses superuser admin context, obtains the sysroot, and delegates all work to the sysroot post-copy update API.

## State and Persistence
Persistent changes are delegated and likely include copied repository/deployment fixups needed after image or filesystem duplication.

## Dependencies and Integration Points
Uses private sysroot headers, admin parsing, and sysroot update APIs. It is intended for image-copy or install workflows.

## Risks
The wrapper exposes a broad operation with no extra validation. Safety depends on the library correctly detecting and updating copied state.

## Test Signals
Image-copy integration tests should verify post-copy updates required metadata and remains idempotent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c -->
