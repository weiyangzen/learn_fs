<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/conf.py -->
## sources/distributed-fs/ceph-client/Documentation/conf.py

### Purpose
Configures the Linux kernel Sphinx documentation build, including extension loading, dynamic include/exclude patterns, theme options, LaTeX/PDF settings, and Sphinx event hooks.

### Important APIs, Types, And Functions
Important objects include kern_doc_dir, needs_sphinx, has_include_patterns, config_init(), have_command(), extensions, c_id_attributes, source_suffix, version/release detection, get_cline_version(), HTML/LaTeX/man/texinfo/epub/pdf settings, add_subproject_index(), and setup().

### Control Flow
At import time it computes Sphinx version support, extension list, math renderer, theme settings from environment, version from Makefile or command line, and static output settings. config_init() adjusts include/exclude patterns relative to app.srcdir and populates latex_documents. setup() connects config-inited and source-read hooks.

### State, Persistence, And Dependencies
Build state is Sphinx config variables and event-time mutations. Persistent outputs are created by Sphinx outside this file. Depends on Sphinx, kernel Documentation/sphinx extensions, tools/scripts paths, environment variables DOCS_THEME/DOCS_CSS/SPHINX_IMGMATH, LaTeX/dvipng availability, and Read the Docs theme packages when selected.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include broad except while parsing ../Makefile, a likely typo encoding="utf=8", mutable global latex_documents, tags global use from Sphinx, and optional theme imports silently falling back to alabaster.

### Test Signals
Test signals include full Documentation build, SPHINXDIRS subproject build, old and new Sphinx include_patterns behavior, DOCS_THEME fallback, imgmath selection, and generated latex_documents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/conf.py -->
