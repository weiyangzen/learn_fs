# sources/cloud-native/ostree/ci/rpmostree.sh

Purpose: integration test script that builds and installs the current libostree, then builds and tests a pinned rpm-ostree tag against it.

Important APIs/functions: `RPMOSTREE_TAG=v2019.4`, helpers from `libbuild.sh`, `CONFIGOPTS`, `build`, `make install`, `git clone --recursive --depth=1 -b`, trap `cleanup`, `make check`, `make vmsync`, and `make vmcheck TESTS=...`.

Control flow: install RPM build/test deps for ostree and rpm-ostree, install duplicate test dependencies, build/install ostree from the current checkout, clone pinned rpm-ostree into a temp dir, build it, preserve test logs on exit, run unit tests, sync to VM, dump VM journal on failure, then run a small vmcheck subset.

State and persistence: mutates system packages and installed ostree binaries, creates temp clone/build state, and copies `test-suite.log`/`vmcheck` back to the original code directory on exit.

Dependencies and integration: cross-project compatibility gate for libostree with rpm-ostree, ansible/SSH VM checks, SELinux policy packages, Rust tooling, Python RPM bindings, and parallel/clang tools.

Risks and test signals: risks include pinned old rpm-ostree masking newer integration issues, VM availability, root/package side effects, and broad package names. Strong signals are rpm-ostree `make check`, `vmsync`, VM journal diagnostics, and selected layering vmchecks.
