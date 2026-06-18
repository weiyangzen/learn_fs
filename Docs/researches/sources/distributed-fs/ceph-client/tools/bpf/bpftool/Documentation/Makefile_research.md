<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile

Purpose: this Makefile builds, installs, cleans, and uninstalls bpftool man pages from reStructuredText sources.

Important targets/variables: `MAN8_RST` collects `bpftool*.rst`, `DOC_MAN8` maps them to `$(OUTPUT)*.8`, and `RST2MAN_DEP` checks for `rst2man`. The `see_also` make function appends a generated SEE ALSO section referencing `bpf(2)`, `bpf-helpers(7)`, and sibling bpftool pages. Targets include `man`, `man8`, pattern `$(OUTPUT)%.8`, `clean`, `install`, and `uninstall`.

Control flow: the default goal `man` builds all man8 pages. Each page concatenates the source `.rst` with generated SEE ALSO text and pipes it through `rst2man --verbose --strip-comments`. Install creates `$(DESTDIR)$(man8dir)` and installs generated pages mode 644.

State and persistence: generated `.8` files are written under `$(OUTPUT)`. Install/uninstall mutate the destination man directory. No source `.rst` files are modified.

Dependencies and integration points: it uses kernel tools `Makefile.include`, `rst2man`, install/rm/rmdir, and is invoked by the parent bpftool Makefile's `doc*` targets.

Risks: missing `rst2man` causes a make-time error only when generating pages. The generated SEE ALSO list depends on current wildcard results and excludes the source page being built by basename filtering. If `OUTPUT` is unset, generated man pages land in the documentation source directory.

Test signals: run `make man`, `make clean`, `make install DESTDIR=...`, and `make uninstall DESTDIR=...`; verify generated pages include SEE ALSO entries and no stale pages remain after clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Documentation/Makefile -->
