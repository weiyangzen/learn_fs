# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_install.sh

Purpose: this helper installs kselftest artifacts by invoking the selftests make install target with `KSFT_INSTALL_PATH` set.

Important APIs and functions: `main()` computes `base_dir=\`pwd\``, defaults `install_dir` to `$base_dir/kselftest_install`, verifies the current directory basename is `selftests`, optionally accepts an existing destination directory argument, and runs `KSFT_INSTALL_PATH="$install_dir" make install`.

Control flow: the script rejects execution outside the selftests top-level directory. With no argument it announces and uses a default install directory under the current tree. With one argument it requires that path to exist, then uses it. It delegates all actual build/install work to `make install`.

State and persistence: it writes no files directly. Persistence is produced by the Makefile install target under `KSFT_INSTALL_PATH`. Its own state is only shell variables.

Dependencies and integration points: depends on Bash, `pwd`, `basename`, a make-capable selftests tree, and the top-level selftests install rules. It is an integration shim for packaging/running selftests outside the source tree.

Risks: it refuses to create a user-specified directory, so automation must pre-create the destination. The default path is inside the source tree, which can dirty the worktree if used casually. The basename check is simple and can reject symlinked or unusual layouts.

Test signals: visible signals are printed install-location messages, an immediate exit with status 1 when cwd/destination validation fails, or the propagated `make install` result.
