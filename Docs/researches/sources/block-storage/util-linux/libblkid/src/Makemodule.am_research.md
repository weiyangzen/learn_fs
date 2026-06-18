# File Research: sources/block-storage/util-linux/libblkid/src/Makemodule.am

## Purpose
Autotools build definition for the libblkid library, its public generated header, test binaries, fuzz target, and install/uninstall hooks.

## Main Components
- Installs generated `libblkid/src/blkid.h` under `$(includedir)/blkid`.
- Builds `libblkid.la` from core modules, partition probers, superblock probers, and topology backends.
- Adds Linux-only topology sources under `if LINUX`.
- Links against `libcommon.la` and optionally `$(ECONF_LIBS)`.
- Adds symbol-version dependency `libblkid/src/libblkid.sym`.
- Applies common, shared-library, and libblkid include flags.
- Applies version-script linker flags when available.
- Adds static test programs for cache, config, device, device-name, device-number, evaluate, read, resolve, save, tag, and verify modules.
- Builds `test_blkid_fuzz` when a fuzzing engine is configured and always builds `test_blkid_fuzz_sample`.
- Provides install/uninstall hooks to relocate `libblkid.so.*` from `$(usrlib_execdir)` to `$(libdir)` when those differ.

## Dependencies and Interactions
This is the Autotools counterpart to `libblkid/meson.build`. It depends on project-level conditionals `BUILD_LIBBLKID_TESTS`, `FUZZING_ENGINE`, `HAVE_ECONF`, `HAVE_VSCRIPT`, and `LINUX`.

## Research Notes
The library source list includes the files in this research group plus many superblock and topology modules outside this group. Test targets are built by compiling individual implementation files with `-DTEST_PROGRAM`, using embedded test mains guarded by that macro.
