<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/docs/Makefile -->
# sources/cloud-native/containers-storage/docs/Makefile

- Purpose: Builds and installs man pages from Markdown documentation.
- Important targets: `docs` builds `.1` pages and `containers-storage.conf.5`; `install` installs `.5` pages under `${PREFIX}/share/man/man5`.
- Control flow and state: Uses `go-md2man` from `../tests/tools/build/go-md2man`, wildcard Markdown inputs, and `install`.
- Dependencies and integration: Called by top-level docs targets and packaging workflows.
- Risks: `MANPAGES_MD` references `docs/*.5.md` while the Makefile itself is already in docs, so path assumptions are sensitive to invocation directory.
- Test signals: Generated man pages exist and package install includes them.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/docs/Makefile -->
