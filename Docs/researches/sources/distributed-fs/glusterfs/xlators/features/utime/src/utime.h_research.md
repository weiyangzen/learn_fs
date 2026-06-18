# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.h

## Purpose
Declares the utime private configuration structure and includes generated fop prototypes.

## Important APIs, Types, and Functions
- `utime_priv_t` contains `gf_boolean_t noatime`.
- Includes `utime-autogen-fops.h` for generated wrapper prototypes.

## Control Flow
No runtime flow.

## State and Persistence
Defines the translator-private in-memory `noatime` flag.

## Dependencies and Integration Points
Depends on `xlator.h`, `defaults.h`, and generated header availability.

## Risks
Generated header must exist before compile. Adding private fields requires lifecycle updates in `init()`, `reconfigure()`, and `fini()`.

## Test Signals
Build generated header and verify noatime option affects generated wrapper behavior.
