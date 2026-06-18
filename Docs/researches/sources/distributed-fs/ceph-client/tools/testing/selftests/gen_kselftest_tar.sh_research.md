<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh

## Purpose
This utility script generates a distributable kselftest installation tarball.

## Important APIs, Types, And Functions
`main()` parses optional format names `tar`, `targz`, `tarbz2`, and `tarxz`, chooses tar flags and extension, creates `kselftest_install/kselftest`, runs `./kselftest_install.sh`, creates the archive, prints a notice, and removes the work directory.

## Control Flow
No argument defaults to gzip. Unknown formats exit `1`. Archive creation runs from the temporary install work parent so the archive root is `kselftest`.

## State And Persistence
It creates and deletes `kselftest_install/` in the current directory and leaves `kselftest.tar*` in the invocation directory.

## Dependencies And Integration Points
It depends on `kselftest_install.sh`, `tar`, and compression support selected by tar flags. It is an older convenience path superseded by `make gen_tar`.

## Risks
The script removes `$install_work` recursively; if path construction or cwd is unexpected, cleanup could be destructive within the working directory. Consumers may parse the final archive-created line, so the warning intentionally appears before it.

## Test Signals
Expected signal is `Kselftest archive kselftest<ext> created!` and a matching non-empty archive in the current directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gen_kselftest_tar.sh -->
