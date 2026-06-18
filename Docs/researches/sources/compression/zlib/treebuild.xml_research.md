# sources/compression/zlib/treebuild.xml

`treebuild.xml` is a declarative build manifest for the zlib package. It declares package version `1.3.2.1`, a `zlib` library with dynamic-library metadata, public headers `zlib.h` and `zconf.h`, install include properties, and source-to-header dependencies.

The manifest covers checksum, compression, gzip, deflate, tree, utility, inflate, inflateBack, inftrees, and inffast sources. A treebuild consumer would parse the XML, install public headers, compile each listed source, and use dependency declarations for rebuild decisions. It does not define tests or example executables.

State is build output rather than runtime state: installed headers, library artifacts, and dependency metadata. Integration points include `zlib.h`, `zconf.h`, `zutil.h`, `deflate.h`, `trees.h`, `gzguts.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Risks are manifest drift from actual source files, stale version metadata, and an inline compiler property marked not implemented. A successful treebuild library build and header install are the main test signals.
