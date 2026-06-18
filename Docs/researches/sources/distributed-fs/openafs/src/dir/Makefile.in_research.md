# sources/distributed-fs/openafs/src/dir/Makefile.in

This Makefile builds and installs the OpenAFS directory package library. It compiles `buffer.o`, `dir.o`, `salvage.o`, and component version into `libdir.a`, installs `dir.h`, and runs the `test` subdirectory build.

Control flow is standard make: `all` builds library, depinstall, and tests; `depinstall` stages `dir.h`; `install` and `dest` install the library under AFS lib directories and the header under include directories; `clean` removes objects, archives, core files, and generated version files. State is the archive and installed header.

Dependencies are config make fragments, LWP settings, archive tools, and the three source files. Integration points are fileserver, volserver, salvager, and test programs that manipulate AFS directory pages. Risks are library consumers depending on external buffer I/O callbacks not visible in this Makefile, and tests only being built rather than necessarily run. Test signals are successful `libdir.a` build, `dir/test/dtest`, and downstream server links.
