# sources/cloud-native/composefs/.github/workflows/ci-bootc.yml

Purpose: reverse-dependency CI that validates composefs changes against bootc install flow.

Important APIs/types/functions: workflow triggers on main push, PR, and manual dispatch; concurrency cancellation; job builds `ci/Containerfile.c9s-bootc`; runs privileged `bootc install to-filesystem --replace=alongside`.

Control flow: checkout, build local test image with podman, then run it privileged against host `/target` and container storage mounts.

State/persistence: mutates the CI runner filesystem target during bootc install, within ephemeral runner lifetime.

Dependencies/integration: GitHub Actions Ubuntu runner, podman, bootc, privileged container execution, and composefs package integration in bootc.

Risks/test signals: high-privilege CI step and host mount coupling. Provides valuable revdep signal but can be brittle on runner environment changes.
