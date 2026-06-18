# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.c

## Purpose
Template C source used to generate `utime-autogen-fops.c`.

## Important APIs, Types, and Functions
- Includes `config.h` defensively and `utime-helpers.h`.
- Contains `#pragma generate`, which the Python generator replaces with generated fop wrappers and callbacks.

## Control Flow
The file itself has no final fop logic until generation. The generator copies surrounding text and replaces the pragma with generated code.

## State and Persistence
No runtime state. It is a source template for generated build artifacts.

## Dependencies and Integration Points
Consumed by `utime-gen-fops-c.py` from `Makefile.am`. Generated code calls `gl_timespec_get()`, `utime_update_attribute_flags()`, and child fops.

## Risks
Removing or misspelling the pragma yields an empty or incomplete generated fops source. Include order affects generated wrappers.

## Test Signals
Generated `utime-autogen-fops.c` should contain `BEGIN GENERATED CODE` and definitions for all selected utime fops.
