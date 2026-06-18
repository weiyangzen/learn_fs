# sources/distributed-fs/lizardfs/utils/cpp-interpreter.sh

Purpose: Bash wrapper that treats a C++ source file as an interpreted test/program by compiling it on demand to a cached executable and then running it.

Important operations: it strips a leading shebang from the source via `grep -v '^#!'`, hashes the remaining source with `md5sum`, chooses `${TEMP_DIR:-/tmp}/cached_c_$hash`, compiles with `c++ -xc++ -o "$executable" - <<< "$source"` if the executable is missing or not executable, and finally executes it with forwarded arguments.

Control flow: the first argument is the source path; all remaining arguments are passed to the compiled binary. Empty source after shebang removal exits with status 1. Compilation failure aborts due to `set -e`.

State and persistence: persists cached binaries in `TEMP_DIR` or `/tmp`, keyed only by source content. It does not include compiler flags, compiler version, include paths, or linked libraries in the cache key.

Dependencies/integration: depends on Bash, GNU `md5sum`, `awk`, a working C++ compiler, and any includes required by the source. Useful for tests that embed small C++ programs with shebang lines.

Risks and test signals: cache collisions are unlikely but possible with MD5, and stale binaries may be reused when only compiler flags/environment changed. `grep -v '^#!'` removes all shebang-like lines, not just the first. Test signals are first compile, cached rerun, forwarding of arguments, failure on invalid C++, and honoring `TEMP_DIR`.
