# sources/control-plane/rook/.github/workflows/canary-integration-suite.yml

Purpose: reusable workflow entry point for Rook canary integration tests.

Important configuration and control flow: triggers on pushes to tags `v*`, branches `master` and `release-*`, and pull requests targeting `master` or `release-*`, ignoring documentation and design path changes for PRs. It uses strict bash defaults, cancels superseded runs, grants contents read, and defines a single `canary-tests` job that calls `./.github/workflows/canary-integration-test.yml` with `ceph_images: ["quay.io/ceph/ceph:v19"]` and inherited secrets.

State, dependencies, and integration: state is delegated to the reusable canary workflow and its cluster/test resources. It depends on the called workflow contract accepting `ceph_images` and inherited secrets. It integrates release branches, tags, and PR validation.

Risks and test signals: changes outside ignored docs/design paths can trigger expensive integration jobs. The Ceph image is fixed to v19, so coverage tracks that version only unless updated. Signals are pass/fail results from the reusable workflow.
