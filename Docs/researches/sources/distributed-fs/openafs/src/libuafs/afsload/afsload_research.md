## sources/distributed-fs/openafs/src/libuafs/afsload/afsload

Purpose: Shell front-end for running libuafs load tests under MPI.

Important logic: Defines installed paths for `afsload_check.pl`, `afsload_run.pl`, and Perl include path, reads `MPIRUN` and `LIBMPI` environment overrides, parses `-q`, `-p <nprocs>`, and `-t <test.conf>`, optionally validates the config, then launches MPI with one additional director process.

Control flow: `-p` is incremented by one because rank 0 is the director. Unless `-q` is set, it runs the checker with the expanded process count. It verifies `mpirun` exists and `LIBMPI` is a file, then runs `mpirun -np "$procs"` with `/bin/sh -c "LD_PRELOAD=$LIBMPI $ALPERL $ALRUN $conf"`.

State and persistence: Writes no state directly. The invoked Perl runner writes per-node logs according to config and mutates AFS test paths.

Dependencies and integration: Depends on MPI, a preloadable MPI library, installed afsload Perl modules, and the libuafs Perl binding.

Risks: Paths are hard-coded to `/usr/local/lib/afsload`. The shell command embeds `$conf` in a string, so whitespace or shell metacharacters in the config path are risky. It assumes `LD_PRELOAD` is the correct MPI binding mechanism.

Test signals: CLI validation, quiet vs checked mode, missing mpirun, missing LIBMPI, process count adjustment, config paths with spaces, and full simple.conf execution.
