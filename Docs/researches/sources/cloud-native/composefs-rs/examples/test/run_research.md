# sources/cloud-native/composefs-rs/examples/test/run

Purpose: wrapper to build one example image for a given OS and run the pytest VM tests against it.

Important APIs/types/functions: positional `EXAMPLE` and `OS`; invokes `"${EXAMPLE}/build" "${OS}"`; sets `TEST_IMAGE="${EXAMPLE}/${OS}-${EXAMPLE}-efi.qcow2"` and runs `pytest test`.

Control flow: changes to examples root, builds image, then launches tests with the image path in the environment.

State/persistence: produces example qcow2 images via the build script and consumes them in tests.

Dependencies/integration: depends on example-specific `build` scripts, pytest configuration, and `test_basic.py`.

Risks/test signals: naming convention must match each build script output. Failure to build stops tests due to `set -eux`.
