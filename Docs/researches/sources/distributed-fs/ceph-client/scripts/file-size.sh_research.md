# sources/distributed-fs/ceph-client/scripts/file-size.sh

Purpose: Prints the byte size of a file using `ls -dn` field parsing.

Important APIs/functions: Runs `set -- $(ls -dn "$1")` and prints `$5`.

Control flow: One positional file argument is passed to `ls`; shell fields are reassigned to ls output tokens; fifth field is printed.

State/persistence: Stateless and read-only.

Dependencies/integration: POSIX shell and `ls`. Used where a simple file size helper is needed in build scripts.

Risks: Parses `ls` output, which is less robust than `stat`; unusual implementations or locale/format changes can break it. Missing argument or nonexistent file behavior is delegated to `ls`.

Test signals: Regular files, symlinks, missing file, names with spaces, and host variants where `ls -dn` output differs.
