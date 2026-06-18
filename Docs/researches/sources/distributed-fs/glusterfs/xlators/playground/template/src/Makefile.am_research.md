# sources/distributed-fs/glusterfs/xlators/playground/template/src/Makefile.am

## Purpose
Defines the build recipe for the playground template xlator.

## Important APIs, Types, And Functions
Builds `template.la` from `template.c`, installs under `xlator/playground`, links `libglusterfs.la`, and declares `template.h` as a private header.

## Control Flow
Automake compiles the module using Gluster and RPC/XDR include paths.

## State And Persistence
No runtime state. It controls installed module location.

## Dependencies And Integration Points
Uses Gluster xlator module flags and libglusterfs.

## Risks
As a template, it is intentionally skeletal. Accidentally enabling it in a production graph would add no real fops.

## Test Signals
Build should produce a loadable `template.la`; loading it should exercise init and option parsing only.
