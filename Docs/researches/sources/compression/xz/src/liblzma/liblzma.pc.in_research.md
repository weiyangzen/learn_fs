# sources/compression/xz/src/liblzma/liblzma.pc.in Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/liblzma.pc.in -->
## sources/compression/xz/src/liblzma/liblzma.pc.in

### Purpose
`liblzma.pc.in` is the pkg-config template for liblzma consumers.

### Important APIs, Types, And Functions
It defines substitution variables for install prefix, library directory, include directory, package URL/version, public C flags, static API C flags, public libs, and private libs.

### Control Flow
There is no runtime flow. Configure substitutes `@prefix@`, `@PACKAGE_VERSION@`, `@PTHREAD_CFLAGS@`, and related variables into the installed `.pc` file.

### State, Persistence, And Dependencies
The installed `.pc` file persists build/install metadata for downstream build systems. `Libs.private` carries extra libraries needed for static linking.

### Integration Points
Downstream projects call `pkg-config --cflags --libs liblzma` or `--static` and receive include/library flags from this template.

### Risks
Incorrect `Libs.private` or `Cflags.private` can break static consumers. `Cflags.private: -DLZMA_API_STATIC` changes symbol import/export behavior and must stay aligned with headers.

### Test Signals
Install-tree tests should run `pkg-config --modversion`, dynamic link checks, and static link checks against a trivial program using `lzma_version_number()`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/liblzma.pc.in -->
