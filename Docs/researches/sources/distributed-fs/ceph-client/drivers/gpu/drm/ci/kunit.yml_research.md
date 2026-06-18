# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.yml

Purpose: defines GitLab CI jobs that run DRM KUnit tests on arm32, arm64, and x86_64 with LLVM and QEMU.

Important jobs/templates: `.kunit-packages` installs clang/lld/llvm for `$LLVM_VERSION`. `.kunit-base` runs in the `kunit` stage with 30 minute timeout, shallow clone depth, and script `drivers/gpu/drm/ci/kunit.sh`. `kunit:arm32`, `kunit:arm64`, and `kunit:x86_64` extend the corresponding build templates, add the shared LLVM packages, and install `qemu-system-arm`, `qemu-system-aarch64`, or `qemu-system-x86`.

Control flow: jobs inherit build rules and architecture variables from `.build:*`, so scheduling follows the top-level CI policy.

State and persistence: no explicit artifacts; KUnit output appears in job logs.

Dependencies and integration points: depends on `build.yml` templates, Debian package availability, `kunit.sh`, LLVM version from imported containers, and kernel KUnit infrastructure.

Risks: no artifacts are collected for postmortem beyond logs. QEMU package names can change with Debian base images. KUnit failures and infrastructure failures both fail the job unless logs are inspected.

Test signals: all three jobs expand with correct `KERNEL_ARCH`, packages install, `kunit.py run` boots each architecture, and failure logs clearly show failing KUnit cases.
