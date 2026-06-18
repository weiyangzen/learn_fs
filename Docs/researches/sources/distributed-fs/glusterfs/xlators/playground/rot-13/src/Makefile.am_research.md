# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/Makefile.am

## Purpose
Defines the build recipe for the sample ROT13 xlator.

## Important APIs, Types, And Functions
Builds `rot-13.la` from `rot-13.c`, installs under `xlator/encryption`, links `libglusterfs.la`, and declares `rot-13.h` as a private header.

## Control Flow
Automake compiles with Gluster and RPC/XDR include paths and xlator module linker flags.

## State And Persistence
No runtime state. The install path categorizes this sample as encryption rather than playground.

## Dependencies And Integration Points
Uses `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and libglusterfs.

## Risks
The install category differs from its source-tree playground location. Since the translator is sample-quality and not production-safe, accidental installation/loading is a risk if build traversal includes it.

## Test Signals
Direct module build should produce `rot-13.la`; packaging should verify whether installing this sample is desired.
