# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/fops-tmpl.c

## Purpose

`fops-tmpl.c` is the template input for generating metadisp's default fop wrappers and fop table.

## Important APIs, Types, and Functions

The file includes `config.h`, `metadisp.h`, and `metadisp-fops.h`, then contains `#pragma generate`, which `gen-fops.py` replaces with generated C.

## Control Flow

There is no standalone runtime flow in the template. During build, lines are copied until the pragma, then generated fop functions and the `struct xlator_fops fops` table are emitted.

## State and Persistence Behavior

No runtime state is owned here. The persistent build artifact is generated `fops.c`.

## Dependencies and Integration Points

The template depends on `gen-fops.py` and libglusterfs's Python generator substitution tables. It also depends on hand-written declarations in `metadisp-fops.h` for fops excluded from generation.

## Risks and Edge Cases

The pragma is a single build-generation anchor. Removing or misspelling it yields a `fops.c` without generated wrappers. Include-order changes can break generated code that relies on metadisp macros and prototypes.

## Test Signals

A clean build should produce `fops.c` containing generated code between the begin/end comments and a complete `fops` table. Compile warnings in generated fops are a strong signal of template or generator drift.
