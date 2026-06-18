# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.h

## Purpose
Template header used to generate prototypes for utime fop wrappers.

## Important APIs, Types, and Functions
- Include guard `_UTIME_AUTOGEN_FOPS_H`.
- Contains `#pragma generate`, expanded by `utime-gen-fops-h.py`.

## Control Flow
No runtime flow. Generator replaces pragma with fop prototypes.

## State and Persistence
No state.

## Dependencies and Integration Points
Used by `Makefile.am` as source for `utime-autogen-fops.h`, included by utime implementation through generated build integration.

## Risks
Missing pragma or guard changes can break symbol declarations or duplicate inclusion.

## Test Signals
Build should generate prototypes matching generated C definitions.
