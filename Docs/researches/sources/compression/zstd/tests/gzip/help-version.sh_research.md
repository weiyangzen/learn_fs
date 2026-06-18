<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/help-version.sh -->
## sources/compression/zstd/tests/gzip/help-version.sh

Purpose: Imported GNU test ensuring built programs behave correctly for `--help`, `--version`, and a minimal normal invocation. In this zstd gzip test directory it primarily validates gzip-family wrapper behavior when included in `built_programs`.

Important APIs and functions: Requires `built_programs`, `VERSION`, and `PACKAGE_BUGREPORT` environment variables. Sources `init.sh` and uses `path_prepend_ .`, program-specific setup functions such as `zcat_setup`, `zdiff_setup`, `zgrep_setup`, and generic helpers like `grep`, `compare`, and `Exit`.

Control flow: It first extracts the version from the first built program and checks it against `$VERSION`. For locales `C`, `fr`, and `da`, it runs each program with `--help` and `--version`, verifies help mentions the bug-report address, and checks that writes to `/dev/full` fail with expected statuses. It then creates per-program fixtures and runs each program once with minimal arguments, skipping programs known to be unsuitable.

State and persistence: Creates a nested temporary directory plus files such as `zin.gz`, `zin2.gz`, `bigZ-in.Z`, input/output fixtures, and helper directories. All are under the `init.sh` temporary directory.

Dependencies and integration points: Integrates with Automake/Coreutils-style test variables and host tools. It expects gzip helper programs (`zcat`, `zcmp`, `zdiff`, `zgrep`, etc.) to be discoverable through `PATH`, with compressed fixtures produced by the tested `gzip`.

Risks: This file is more generic than the zstd gzip subset and contains many setup functions for programs zstd may not build. Incorrect `built_programs` can make the test irrelevant or fail on unrelated utility behavior. Locale-dependent output is intentionally tested, so translated builds must still include bug-report text.

Test signals: Version mismatch, missing bug-report text, unexpected success writing to `/dev/full`, bad exit status, or failed minimal command invocation sets `fail=1`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/help-version.sh -->
