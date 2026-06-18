# sources/control-plane/mayastor/.github/workflows/pr-commitlint.yml

## Purpose
Validates commit messages on pull requests and staging branch pushes.

## Important Jobs and Steps
`commitlint` checks out full history, installs `@commitlint/config-conventional` and `@commitlint/cli`, then for PRs calculates base/head SHAs, force-enables the custom code-review rule by editing `commitlint.config.js`, runs `npx commitlint --from ... --to ... -V`, and fails on duplicate commit subjects. For staging branch it succeeds without linting PR commits.

## Control Flow
Triggers on PR opened/edited/reopened/synchronize and push to `staging`. Branch comparison is skipped for `refs/heads/staging`.

## State and Persistence
Mutates the checked-out `commitlint.config.js` in the runner only. Writes a temporary `subjects` file. Does not push changes.

## Dependencies and Integration Points
Depends on npm, commitlint config, full git history, and GitHub PR event fields. Provides required status listed in `bors.toml`.

## Risks
The shell test `if [ ! ${{ github.ref }} = "refs/heads/staging" ]; then` is unquoted and can be brittle. Editing config with sed assumes exact text. Duplicate subject detection can reject legitimate fixup/split commits.

## Test Signals
Open PRs with valid/invalid commit subjects, code-review wording, and duplicate subjects. Staging branch should not fail due to missing PR fields.
