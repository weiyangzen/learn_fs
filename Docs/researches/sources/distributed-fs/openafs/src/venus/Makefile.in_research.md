# sources/distributed-fs/openafs/src/venus/Makefile.in

Purpose: Autoconf Makefile template for building and installing OpenAFS venus/client command programs.

Important targets and variables: Defines `PROGRAMS` including `afsio`, `cacheout`, `cmdebug`, `fs`, `fstrace`, `gcpags`, `livesys`, `twiddle`, `up`, and `whatfid`. Library groups include `AFSIO_LIBS`, `FSLIBS`, `CMLIBS`, and default `LIBS`. Link targets use `LT_LDRULE_static` with fsint, vlserver, rxkad, cmd, util, opr, roken, pthread, hcrypto, and Kerberos libraries as needed.

Control flow and state: The build flow includes configured `Makefile.config` and `Makefile.pthread`, builds all programs, compiles special generated `afscbint.ss.o`, installs selected binaries into bindir/sbindir/afssrvbindir, and places legacy destination-tree copies under `${DEST}`. `clean` removes build artifacts; `test` descends into a `test` subdirectory.

Dependencies and integration: Integrates venus command sources with generated component version files and many OpenAFS libraries. It is a central bridge between util library outputs and user-facing client tools like `fs`, `cmdebug`, and `fstrace`.

Risks and test signals: Some programs are built but intentionally not installed (`cacheout`, `gcpags`, `twiddle`, `whatfid`). Link library ordering is important for static builds. Install paths duplicate `fs` into both server and user bindirs. Test signal is successful `make`, `make install`/`dest`, and `make test` in the venus subtree.
