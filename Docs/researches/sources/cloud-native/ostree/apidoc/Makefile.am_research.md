<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/Makefile.am -->
## sources/cloud-native/ostree/apidoc/Makefile.am

### Purpose
This gtk-doc makefile builds the libostree API reference from public headers and C sources.

### APIs, Types, and Control Flow
It includes public header definitions, sets `DOC_MODULE=ostree`, points `DOC_MAIN_SGML_FILE` at `ostree-docs.xml`, scans `src/libostree`, configures gtk-doc scan/mkdb options, computes header and C globs, lists private headers to ignore, and generates `version.xml` from `$(VERSION)`. It includes the standard `gtk-doc.make`, distributes `version.xml` and section files, and adds generated doc files to gitignore metadata.

### State, Dependencies, and Integration
Generated state includes gtk-doc XML/HTML artifacts and `version.xml`. It integrates with top-level docs subdir inclusion, `Makefile-libostree-defines.am`, `gtkdocize`, and the docs GitHub workflow.

### Risks and Test Signals
The ignore list must be maintained to avoid documenting private headers. `HFILE_GLOB` spans source and build dirs for generated version headers. Test signal is `make -C apidoc` under `--enable-gtk-doc` and docs workflow success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/Makefile.am -->
