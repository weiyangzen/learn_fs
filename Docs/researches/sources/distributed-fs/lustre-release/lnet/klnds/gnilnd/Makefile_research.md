# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/Makefile

## Purpose
This Kbuild makefile builds the Cray/HPE GNI LNet Network Driver module.

## Important APIs, Types, And Functions
`obj-m += kgnilnd.o` declares the module. `kgnilnd-objs` links `gnilnd.o`, callbacks, module parameters, debug/proc/sysctl, stack, and connection objects. `ccflags-y` defines `SVN_CODE_REV` as a Kbuild string and appends `$(GNICPPFLAGS)`. `CONFIG_GCOV_PROFILE_LNET` enables `GCOV_PROFILE`.

## Control Flow
When selected by the parent `klnds/Makefile`, Kbuild compiles each listed GNILND object and links them into `kgnilnd.o`, applying GNI-specific compiler flags.

## State, Persistence, And Dependencies
No runtime state exists in the makefile. Build behavior depends on `GNICPPFLAGS`, `SVN_CODE_REV`, kernel config, and the listed GNILND source files.

## Integration Points
It is selected through `CONFIG_LNET_GNILND` and contributes the legacy GNI LND module to the LNet build.

## Risks
Missing `GNICPPFLAGS` or incompatible GNI headers can fail compilation. Removing any object from the list can drop debug, sysctl, stack, connection, or callback functionality. `SVN_CODE_REV` quoting must remain Kbuild-safe.

## Test Signals
Build tests should compile with representative GNI flags, with and without GCOV, validate all expected object files are linked, and confirm the generated module exports the expected version/debug metadata.
