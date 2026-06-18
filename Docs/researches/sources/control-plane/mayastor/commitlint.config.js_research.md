# sources/control-plane/mayastor/commitlint.config.js

## Purpose
Commitlint configuration enforcing conventional commit types, formatting, and a custom rule preventing review-fixup commits from being merged.

## Important APIs and Rules
Exports default JS object with `rules`, `defaultIgnores: false`, `ignores`, and `plugins`. Type enum allows build/chore/ci/docs/feat/fix/perf/refactor/revert/style/test/example/security. Subject/body/footer/header length and casing rules are configured. Custom plugin rule `code-review-rule` rejects subjects containing `code-review`, `review comment`, `address comment`, or `addressed comment`.

## Control Flow
Commitlint loads this module and invokes configured rules per commit message. Ignore functions bypass bors and merge-pull-request messages.

## State and Persistence
No runtime state. CI may modify the checked-out copy with sed to enforce the code-review rule in PR validation.

## Dependencies and Integration Points
Used by pre-commit and `.github/workflows/pr-commitlint.yml`. Depends on commitlint supporting ESM default export and plugin object format.

## Risks
`defaultIgnores: false` means many generated commit types are linted unless custom ignores catch them. Subject substring matching can reject legitimate descriptions. CI sed mutation assumes exact text layout.

## Test Signals
Run `npx commitlint` over sample valid/invalid messages, including bors merge messages and review-fixup subjects.
