# sources/cloud-native/nydus-snapshotter/.github/codecov.yml

Purpose: Codecov status and comment policy.

Structure and flow: disables patch status, enables project status with auto target and 0.3 percent threshold, posts comments only when coverage changes, and waits for CI without requiring CI to pass before notification.

State and dependencies: external Codecov service configuration; no runtime state in the project.

Integration points: paired with the CI coverage job uploading `coverage.txt`.

Risks and tests: comments indicate validation should be done with Codecov's validate endpoint. A loose patch policy avoids blocking small changes but can miss localized coverage regressions.
