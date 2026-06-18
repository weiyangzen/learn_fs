# sources/distributed-fs/lizardfs/src/tools/CMakeLists.txt

Purpose: Builds and installs the `lizardfs` tools executable plus compatibility symlinks for historical `mfs*` command names.

Important APIs/types/functions: `collect_sources(TOOLS)`; executable `lizardfs`; target link to `mfscommon`; `MFSTOOL_LINKS`; installation of `mfstools.sh`; custom targets that create symlinks to the wrapper script.

Control flow: CMake collects sources, builds one binary from tool sources, installs it, installs the wrapper script, and creates/install symlinks named like `mfsgetgoal`, `mfsfileinfo`, and `mfsrepquota`.

State and persistence: Build-system state only. It writes generated symlink files in the build directory and installs files into `${BIN_SUBDIR}`.

Dependencies and integration: Depends on repository CMake helpers and `mfscommon`. Integrates command dispatch in `main.cc` with legacy executable names through `mfstools.sh`.

Risks and test signals: Symlink creation assumes `ln -sf` and Unix semantics. Missing a tool from `MFSTOOL_LINKS` can break compatibility even if the command exists in `lizardfs`. Build/install tests would catch target/link errors.
