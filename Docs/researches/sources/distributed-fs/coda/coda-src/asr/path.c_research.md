# sources/distributed-fs/coda/coda-src/asr/path.c

Purpose: Implements a Mach-style `path(3)` splitter for environments that do not provide it, splitting a pathname into directory and final component.

Important APIs/functions: `path(char *pathname, char *direc, char *file)`.

Control flow: Handles empty path, no-slash path, and root path as special cases. For general paths, it copies the path, uses `strtok` to find the last component, copies that to `file`, then truncates the directory copy and strips trailing slashes except root.

State and persistence: Pure string manipulation with caller-provided buffers; no persistent state.

Dependencies and integration: Used by ASR object/dependency/argument parsing and resolver argument handling to normalize rule paths.

Risks and test signals: Uses `strtok`, so it is not reentrant and mutates the temporary copy. It assumes destination buffers are large enough and does not bound `strcpy`. Edge cases around repeated slashes depend on `strtok` behavior.
