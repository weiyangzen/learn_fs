<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-ostree.am -->
## sources/cloud-native/ostree/Makefile-ostree.am

### Purpose
This fragment builds the `ostree` command-line binary and its subcommand source graph.

### APIs, Types, and Control Flow
It adds `ostree` to `bin_PROGRAMS`, lists main command sources, generated `parse-datetime.c` from yacc, admin subcommands, remote subcommands, optional GPG signing/import/list sources, optional pull/cookie sources for curl/libsoup, and optional libarchive flags. Shared command CFLAGS include libotutil/libostree/ostree include paths and `PKGLIBEXECDIR`; shared LDADD links `libglnx`, `libotutil`, `libostree-1`, GLib/GIO, bsdiff, and systemd.

### State, Dependencies, and Integration
The generated parser is written under `src/ostree/parse-datetime.c` and cleaned. The binary links to the library built by `Makefile-libostree.am` and is consumed by tests through symlinks in `Makefile-tests.am`.

### Risks and Test Signals
Subcommand source registration is manual, so adding a builtin requires updating this file and likely man/tests. Fetcher conditionals must match library fetcher availability. Test signals are CLI build, parser regeneration, command help tests, and broad shell integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-ostree.am -->
