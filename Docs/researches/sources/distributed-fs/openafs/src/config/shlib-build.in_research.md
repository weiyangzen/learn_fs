# sources/distributed-fs/openafs/src/config/shlib-build.in

This autoconf-substituted shell script builds shared libraries without using libtool. It parses `-d <srcdir>`, `-f <filename>`, `-l <library>`, `-M <major>`, `-m <minor>`, `-i`, `-p`, then `--` followed by linker arguments. It computes the output filename and SONAME, derives export/version-map flags, prints the linker invocation, and executes `@SHLIB_LINKER@`.

Control flow is platform-specific by `@AFS_SYSNAME@`: AIX converts `.map` globals to `.exp` and uses `-bE`; Solaris uses map files and optional `= EXTERN` rewriting under `-i`; Linux passes `--version-script` and `-h`; HP-UX uses `.hp` export control; Darwin builds `_`-prefixed exported symbol lists and may add `-undefined dynamic_lookup`; unknown platforms just link.

State and persistence are generated shared objects and temporary export/map files in the build directory. Dependencies include `awk`, `sed`, platform linkers, generated map files, and autoconf substitutions. Integration points are library Makefiles using `SHLIB_BUILD`. Risks include fragile shell precedence in validation, unsanitized generated files, platform linker flag drift, and silent ABI exposure changes when map files are missing. Test signals are shared-library build/install tests on each supported OS, SONAME/symlink verification, and exported-symbol diffs.
