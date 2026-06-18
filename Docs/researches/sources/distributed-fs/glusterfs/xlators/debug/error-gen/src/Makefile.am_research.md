# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/Makefile.am

## Purpose
This Automake file builds and installs the `error-gen` debug translator module.

## Important APIs, Types, And Functions
It declares `xlator_LTLIBRARIES = error-gen.la`, installs under the debug xlator directory, sets module linker flags, uses `error-gen.c`, links against `libglusterfs.la`, and includes `error-gen.h` and `error-gen-mem-types.h` as non-installed headers. It sets GlusterFS and RPC XDR include paths and builds with `-Wall`.

## Control Flow
Automake compiles the single source into a loadable xlator module and installs it where the GlusterFS translator loader expects debug modules.

## State And Persistence Behavior
No runtime state is held in this build file. It controls build artifacts only.

## Dependencies And Integration Points
It depends on libglusterfs and top-level GlusterFS build variables. It is reached from `xlators/debug/error-gen/Makefile.am`.

## Risks
Missing include paths or incorrect linker flags would break the module. Header list drift can cause distribution or clean builds to miss files.

## Test Signals
`make`, install/package tests, and module-load smoke tests should confirm `error-gen` is built and discoverable.
