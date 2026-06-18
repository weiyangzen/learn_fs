# sources/cloud-native/moby/hack/validate/pr-gh-references

## Purpose
Rejects GitHub issue or PR references in commit messages, encouraging commit-hash references instead.

## Important APIs and Types
Uses regexes for shorthand `#123`, repo refs, owner/repo refs, GitHub URLs, and `check_references`.

## Control Flow, State, and Persistence
For each changed non-empty commit, the script scans the commit body for forbidden references. It emits GitHub Actions error lines and exits nonzero if any are found.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `.validate` and git logs. Risks include regex false positives in prose or code snippets, false negatives for unusual URL forms, and blocking historical references during backports. CI validation is the signal.
