# sources/distributed-fs/ceph-client/fs/ntfs3/Makefile

## Purpose
Builds the `ntfs3` filesystem object and applies warning flags intended to keep the driver clean under a subset of `W=1` diagnostics.

## Important APIs, Types, And Functions
`obj-$(CONFIG_NTFS3_FS) += ntfs3.o` links the driver. `ntfs3-y` lists core objects including attribute, bitmap, directory, logfile, inode, index, runlist, superblock, upcase, and xattr code. `ntfs3-$(CONFIG_NTFS3_LZX_XPRESS)` conditionally adds decompression library objects. `subdir-ccflags-y`, `condflags`, and `ccflags-y` configure warning behavior.

## Control Flow
The kernel build system expands the config-controlled object lists. Optional compiler flags are included via `cc-option` only when supported.

## State And Persistence
No runtime state is owned here. Build composition determines which code paths exist in the resulting kernel or module.

## Dependencies And Integration Points
Depends on Kbuild, `CONFIG_NTFS3_FS`, `CONFIG_NTFS3_LZX_XPRESS`, compiler warning support, and all listed source files. The warning flags affect every source in the subdirectory.

## Risks And Edge Cases
Overly strict warnings can expose compiler-version-specific failures; the Makefile mitigates some with `cc-option` and `-Wno-*` suppressions. Missing an object from `ntfs3-y` would cause link failures or missing functionality.

## Test Signals
Build with GCC and Clang across supported configs, with and without LZX/XPRESS, and run `W=1`-style builds to confirm warning flags do not break the module.
