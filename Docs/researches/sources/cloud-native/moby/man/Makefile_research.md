<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/man/Makefile -->
# sources/cloud-native/moby/man/Makefile

Purpose: builds and installs Moby man pages from Markdown sources. Important targets are `all`, `install`, and `clean`, with pattern rules for `man<section>/<page>` outputs. Control flow derives man-section directories from page names, runs the markdown-to-man tooling, installs generated pages under `DESTDIR`/`PREFIX` style paths, and removes generated artifacts on clean. State is generated manpage files in `man*` directories and installed copies. Dependencies include Make, the page list variables from included make context, and `go-md2man` tooling. Risks include fragile section inference, missing tool dependencies, and generated-file churn. Test signal is build-system validation rather than Go tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/man/Makefile -->
