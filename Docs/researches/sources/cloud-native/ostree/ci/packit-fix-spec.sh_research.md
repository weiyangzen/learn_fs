# sources/cloud-native/ostree/ci/packit-fix-spec.sh

Purpose: prepares an RPM spec file for source builds from the current git checkout, used by Packit and container RPM build flows.

Important APIs/functions: optional spec path argument defaulting to `ostree.spec`; `curl -LO` from Fedora dist-git; version derivation using `git describe --tags --match 'v2???.*'`; three `sed -i` edits for `Version:`, Patch lines, and `%autorelease`.

Control flow: download `ostree.spec` if absent, compute a version compatible with RPM by replacing dashes with dots and removing leading `v`, patch the spec's version, comment out patch directives, and replace autorelease with a fixed release expression.

State and persistence: mutates the spec file in place and may create it from the network. No rollback file is produced.

Dependencies and integration: integrates Fedora dist-git packaging with current upstream snapshots, Packit, and `ci/rpmbuild-cwd`.

Risks and test signals: risks include broad `sed` expressions commenting every `Patch` line, spec format changes, network dependency on dist-git, and mismatched snapshot tarball names. Test signals are successful `rpmbuild -bs/-ba` and Packit SRPM creation.
