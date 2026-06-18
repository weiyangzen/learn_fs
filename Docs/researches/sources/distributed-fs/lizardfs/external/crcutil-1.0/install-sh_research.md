<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh

## Purpose
Portable Automake-style `install-sh` replacement used by the vendored crcutil package when the platform does not provide a sufficiently compatible BSD/GNU `install` program. It installs files, installs multiple files into a directory, creates directories, optionally strips binaries, sets owner/group/mode, and supports copy-on-change semantics.

## Important APIs, Types, and Functions
The script interface accepts `-c`, `-C`, `-d`, `-g GROUP`, `-m MODE`, `-o USER`, `-s`, `-t DIRECTORY`, `-T`, `--help`, and `--version`. Environment variables such as `CHGRPPROG`, `CHMODPROG`, `CHOWNPROG`, `CMPPROG`, `CPPROG`, `MKDIRPROG`, `MVPROG`, `RMPROG`, and `STRIPPROG` override tool paths. Internal shell variables build command fragments like `chgrpcmd`, `chmodcmd`, `chowncmd`, `stripcmd`, and track destination mode through `dir_arg`, `dst_arg`, and `no_target_directory`.

## Control Flow, State, and Persistence
Argument parsing separates directory creation from file installation and peels the final argument into the destination unless `-d` or `-t` already defines it. Directory creation probes whether `mkdir -p` is POSIX-compatible for the current mode/umask and falls back to stepwise prefix creation with quoted path segments. File installation copies to a temporary file in the destination directory, applies owner/group/strip/chmod, compares metadata and content under `-C`, then renames into place or unlinks/moves aside the prior destination if `mv -f` fails. Persistence is entirely filesystem side effects: created directories, installed files, mode/owner/group changes, and temporary files cleaned by traps.

## Dependencies and Integration Points
It depends on POSIX `/bin/sh`, common core utilities, `dirname` with `expr`/`sed` fallbacks, and shell traps. The crcutil Autotools-generated build can invoke it through generated Makefiles during `make install`, independent of the larger LizardFS CMake build.

## Risks and Test Signals
Risks include shell quoting edge cases, races during concurrent directory creation, platform-specific `mkdir -m -p` behavior, mode parsing through `expr`, copy-on-change relying on `ls -dlL` field positions, and temporary names colliding in hostile directories. Test signals are installs to existing and missing directories, `-d` multi-directory creation, `-T` rejection of directory targets, `-C` preserving unchanged files, owner/group/mode/strip paths, source or destination names beginning with `-`, and cleanup after interrupted installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh -->
