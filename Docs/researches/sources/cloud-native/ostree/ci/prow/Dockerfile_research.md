# sources/cloud-native/ostree/ci/prow/Dockerfile

Purpose: multi-stage Prow image definition that builds libostree in a Fedora CoreOS buildroot and packages the result into a coreos-assembler image for FCOS e2e testing.

Important APIs/functions: builder stage `quay.io/coreos-assembler/fcos-buildroot:testing-devel`; runtime stage `quay.io/coreos-assembler/coreos-assembler:latest`; commands `./ci/build.sh`, `make -C target/c install`, `make -C tests/kolainst install`, `rsync`, and symlink of `fcos-e2e.sh` to `/usr/bin/fcos-e2e`.

Control flow: copy repository to `/src`, build and install artifacts into `/cosa/component-install`, build/install kola tests into `/cosa/component-tests`, then in the runtime stage merge those artifacts into `/` and copy CI scripts.

State and persistence: image layers persist built binaries, installed tests, and `/ci` scripts. Runtime user changes from root back to `builder`.

Dependencies and integration: integrates with Prow, coreos-assembler, FCOS buildroot images, `ci/build.sh`, autotools output in `target/c`, and `tests/kolainst`.

Risks and test signals: risks include floating `latest` runtime image, buildroot drift, copying full source context, and rsync overwrites into the runtime root. Signals are successful container build and subsequent `fcos-e2e` execution.
