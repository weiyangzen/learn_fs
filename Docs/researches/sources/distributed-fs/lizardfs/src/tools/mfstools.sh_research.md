# sources/distributed-fs/lizardfs/src/tools/mfstools.sh

Purpose: Compatibility wrapper for legacy `mfs*` tool executable names.

Important APIs/types/functions: Bash `basename $0`; parameter expansion `${tool/lizardfs/lizardfs }`; final command invocation with `"$@"`.

Control flow: The script derives its invoked basename, rewrites the first occurrence of `lizardfs` in the name to `lizardfs `, and runs the resulting command with original arguments. With the listed `mfs*` symlink names, that pattern does not match `lizardfs`, so the wrapper appears to re-invoke the symlink name unless install-time behavior changes the basename/path semantics.

State and persistence: No persistent state.

Dependencies and integration: Installed by `CMakeLists.txt` and used through generated symlinks. Depends on Bash.

Risks and test signals: The substitution expression is terse and appears mismatched with `mfs*` compatibility names, creating a recursion risk. It also does not quote the expanded command word, though installed tool names are controlled. No direct tests in this subset.
