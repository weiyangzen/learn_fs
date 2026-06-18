# sources/control-plane/rook/.github/workflows/stale.yaml

## Purpose

Automates marking and closing stale issues and pull requests.

## Important APIs, Types, and Functions

The `stale` job runs daily at 20:00 UTC in `rook/rook`, grants issue and PR write permissions, and uses `actions/stale` with separate stale/close windows for issues and PRs plus label exemptions.

## Control Flow

On schedule, the action scans issues and PRs, applies `wontfix` to stale issues and `stale` to stale PRs, comments with configured messages, and closes after the configured inactivity windows unless exempt labels are present.

## State and Persistence Behavior

Persistent state is GitHub issue/PR labels, comments, and closed status.

## Dependencies and Integration Points

It integrates with GitHub Issues/PRs, `GITHUB_TOKEN`, and labels `keepalive`, `security`, and `reliability`.

## Risks and Edge Cases

The stale issue label is `wontfix`, which carries semantic meaning beyond stale state. Incorrect label exemptions could close work that should stay active.

## Test Signals

Successful scheduled runs update stale candidates according to policy and leave exempt items untouched.
