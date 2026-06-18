# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-h.py

## Purpose
Generates declarations for all cloudsync fop wrappers.

## Important APIs, types, and functions
Imports operation metadata from `generator.py`, skips `getspec`, and emits one `int32_t cs_<name>(call_frame_t *, xlator_t *, ...)` prototype per operation.

## Control flow
Reads the template path given on argv, replaces `#pragma generate` with generated declarations, and preserves all other template lines.

## State and persistence behavior
No runtime state. Its output persists as build-generated `cloudsync-autogen-fops.h`.

## Dependencies and integration points
Coupled to C generation and to the `cs_fops` table. It relies on `fop_subs` to match current GlusterFS fop signatures.

## Risks and test signals
Signature mismatch with generated C or xlator fops causes compile failures. Test by regenerating from a clean build and validating no stale prototypes remain.
