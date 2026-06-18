# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.h

## Purpose
Header template used by `cloudsync-fops-h.py` to generate prototypes for cloudsync fops.

## Important APIs, types, and functions
It defines include guard `_CLOUDSYNC_AUTOGEN_FOPS_H`, includes GlusterFS xlator plus cloudsync headers, and exposes `#pragma generate` as the insertion point for generated `cs_<fop>()` declarations.

## Control flow
The generator emits “BEGIN GENERATED CODE” and one prototype for every supported operation except `getspec`.

## State and persistence behavior
No runtime state. Generated output is `cloudsync-autogen-fops.h`, included by `cloudsync.h` and compiled users.

## Dependencies and integration points
Coupled to the operation metadata in `libglusterfs/src/generator.py` and to generated C function names.

## Risks and test signals
Prototype drift between generated C and H breaks builds. Test by regenerating both files and compiling all cloudsync fop table references.
