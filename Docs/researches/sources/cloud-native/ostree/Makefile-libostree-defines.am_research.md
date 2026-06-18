<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree-defines.am -->
## sources/cloud-native/ostree/Makefile-libostree-defines.am

### Purpose
This fragment defines the public libostree header set shared by the library build and gtk-doc API documentation.

### APIs, Types, and Control Flow
`libostree_public_headers` lists the installed C API headers such as `ostree.h`, repo/sysroot/deployment APIs, remote/repo-finder APIs, signing APIs, blob reader APIs, and kernel args. `libostree_public_built_headers` identifies generated `src/libostree/ostree-version.h`.

### State, Dependencies, and Integration
The header lists feed `Makefile-libostree.am` installation variables and `apidoc/Makefile.am` gtk-doc scanning inputs. The generated header requires configure/builddir awareness.

### Risks and Test Signals
Forgetting to add a new public header here can omit it from installation and docs. Adding a private header here can expose unsupported API. Test signals include install tree inspection, gtk-doc completeness, and Rust/sys binding generation expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree-defines.am -->
