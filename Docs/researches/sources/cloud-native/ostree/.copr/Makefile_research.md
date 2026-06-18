<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.copr/Makefile -->
## sources/cloud-native/ostree/.copr/Makefile

### Purpose
This COPR-specific makefile builds a source RPM for OSTree in Fedora COPR infrastructure.

### APIs, Types, and Control Flow
The single `srpm` target installs git, marks all git directories safe for containerized builds, runs `ci/make-git-snapshot.sh`, downloads the Fedora rawhide `ostree.spec`, rewrites the spec `Version` from `git describe`, comments downstream patches, replaces `%autorelease`, builds an SRPM with `rpmbuild -bs`, and moves the output to `$outdir`.

### State, Dependencies, and Integration
It writes `ostree.spec`, spec backup files from `sed -ie`, build directories under `.build`, and an SRPM artifact. It integrates with COPR's expected `$outdir`, Fedora dist-git specs, and the repository's snapshot script.

### Risks and Test Signals
It relies on network access to src.fedoraproject.org and mutable rawhide spec content. `git config --global --add safe.directory '*'` is pragmatic in CI but broad. Test signal is a successful COPR SRPM build; failures will usually appear as missing spec, bad version substitution, or rpmbuild dependency/spec errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.copr/Makefile -->
