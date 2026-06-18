# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/Makefile.am

## Purpose
Defines the build recipe for the login authentication module.

## Important APIs, Types, And Functions
Builds `login.la` from `login.c`, installs it in the auth module directory, links `libglusterfs.la`, and includes libglusterfs, protocol server, and XDR headers.

## Control Flow
Automake compiles a single auth module source with module linker flags.

## State And Persistence
No runtime state; install path controls module discovery.

## Dependencies And Integration Points
Depends on `authenticate.h` from protocol server and libglusterfs dict/logging helpers.

## Risks
Wrong `authdir` or missing server include path prevents dynamic loading or compilation.

## Test Signals
Build should produce `login.la`; protocol server should be able to load the auth module.
