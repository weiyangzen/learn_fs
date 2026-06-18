# sources/cloud-native/nydus/.github/codecov.yml

## Purpose
This config defines Codecov thresholds and comment behavior for Nydus coverage reporting.

## Important APIs, Types, and Functions
- Project coverage is enabled with a `70%` target and `0%` threshold.
- Patch coverage is enabled with an `80%` target and `0%` threshold.
- PR comments use layout `"reach, diff, flags, files"`, default behavior, and only post when coverage changes.
- `codecov.require_ci_to_pass` is false while `notify.wait_for_ci` is true.

## Control Flow
Codecov consumes this YAML after CI uploads coverage artifacts. It calculates project and patch statuses and controls whether a comment is posted.

## State and Persistence
Codecov stores coverage results externally. The repository file only controls policy.

## Dependencies and Integration Points
It integrates with `.github/workflows/smoke.yml`, whose coverage jobs upload `codecov.json`, Go `coverage.txt`, and smoke coverage files through `codecov/codecov-action`.

## Risks and Edge Cases
With `threshold: 0%`, any drop below target can fail the Codecov status. Since `require_ci_to_pass` is false, Codecov may process independently of CI success, but `wait_for_ci` delays notification. The validation comment notes the external Codecov validator should be used after changes.

## Test Signals
The config itself is validated by Codecov's validator endpoint and by observing PR coverage statuses/comments after workflow runs.
