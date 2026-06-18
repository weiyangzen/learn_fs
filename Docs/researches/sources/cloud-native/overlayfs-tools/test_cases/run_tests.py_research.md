# sources/cloud-native/overlayfs-tools/test_cases/run_tests.py

Purpose: Meson test runner that builds overlayfs-tools test fixtures and compares generated diff output with expected files.

Important APIs/types/functions: `run_command(cmd)` wraps `subprocess.run(shell=True, check=True)` and exits with the failed return code; command list runs clean, fixture extraction, output generation, and expected generation.

Control flow: sequentially runs Ninja targets for clean/permanent/changes/diff/verbose/overlayed/brief expected/brief output, then runs three `diff -u` comparisons.

State and persistence: creates and removes build-tree fixture directories/files through Ninja targets; writes `diff.out`, `verbose.out`, `brief.out`, and `brief.expected`.

Dependencies/integration: invoked by Meson `test('run_tests', ...)`; assumes Ninja build directory and test fixtures from `meson.build`.

Risks: uses shell strings and sudo-dependent targets; failure stops at first command, which is simple but gives limited aggregate diagnostics.

Test signals: this is the primary automated signal for normal, verbose, and brief diff behavior.
