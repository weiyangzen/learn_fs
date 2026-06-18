# sources/distributed-fs/openafs/src/vol/nfs.h

## Purpose
Provides legacy volume-layer type aliases and simple constants originally shared with NFS-oriented code. It normalizes boolean-like constants, the `private` alias, fixed-width byte/word typedefs, the `Device` type, and the `Error` macro used by older volume and salvage modules.

## Important APIs, Types, And Functions
The header defines `private` as `static`, `TRUE`, `FALSE`, `bit32`, `bit16`, `byte`, `Device`, and conditionally `Error`. `Device` is a `bit32` and represents a Unix device number or the NAMEI partition id/NT drive index abstraction, depending on backend.

## Control Flow
There is no executable flow. Its role is to make older source files compile with consistent names before the richer OpenAFS headers define their own structures and macros.

## State And Persistence
No runtime or persistent state is defined. The `Device` typedef influences persisted metadata indirectly because many volume/inode handle records and salvage structures store device identifiers using this type.

## Dependencies And Integration Points
It includes `errno.h` and assumes `afs_uint32` has been defined by earlier OpenAFS parameter headers. It is included throughout `src/vol`, including partition, NAMEI, purge/nuke, physical I/O, and salvager code.

## Risks And Test Signals
The main risk is macro pollution from legacy names such as `private`, `TRUE`, `FALSE`, and `Error`. Build coverage across C files that include newer system or OpenAFS headers after `nfs.h` is the useful signal.
