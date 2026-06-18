<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Makefile -->
## sources/distributed-fs/ceph-client/Documentation/Makefile

### Purpose
Coordinates Linux kernel Sphinx documentation builds, documentation checks, cleanup, and help output.

### Important APIs, Types, And Functions
Key variables include SPHINXBUILD, SPHINXOPTS, SPHINXDIRS, DOCS_THEME, DOCS_CSS, BUILDDIR, PDFLATEX, LATEXOPTS, PYTHONPYCACHEPREFIX, BUILD_WRAPPER, and FONTS_CONF_DENY_VF. Targets include htmldocs, mandocs, latexdocs, pdfdocs, linkcheckdocs, htmldocs-redirects, refcheckdocs, cleandocs, dochelp, and device-tree binding integration.

### Control Flow
The Makefile conditionally runs missing-document and ABI checks, detects sphinx-build, either emits skip guidance or invokes sphinx-pre-install and sphinx-build-wrapper, and prints dynamic help based on Documentation subdirectories.

### State, Persistence, And Dependencies
Persistent outputs go under $(obj)/output and Python cache prefix. cleandocs removes the build directory. Depends on kernel build variables srctree/obj/Q/PYTHON3, tools/docs scripts, Sphinx, xelatex, dt binding subdir clean integration, and shell utilities.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include shell-based command detection, PATH-dependent Sphinx behavior, linkcheck target network access, and generated output cleanup scope.

### Test Signals
Test signals include make htmldocs with and without Sphinx installed, SPHINXDIRS subset builds, cleandocs, dochelp, WARN_MISSING_DOCUMENTS, and WARN_ABI_ERRORS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Makefile -->
