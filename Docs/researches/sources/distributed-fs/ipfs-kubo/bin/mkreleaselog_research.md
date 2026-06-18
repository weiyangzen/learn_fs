# sources/distributed-fs/ipfs-kubo/bin/mkreleaselog

## Purpose
This Bash release tool generates changelog and contributor statistics for a Kubo release range, including selected dependency changes.

## Important APIs, Types, And Functions
It defines module include/exclude regexes, ignored pathspecs, GitHub handle cache helpers, handle resolution from noreply emails/merge commits/GitHub API, dependency diff helpers (`mod_deps`, `dep_changes`, `resolve_commits`), changelog generation (`release_log`, `recursive_release_log`), stats extraction (`statlog`, `statsummary`), and repository fetching (`ensure`).

## Control Flow
`recursive_release_log` chooses start/end refs, loads handle cache, creates a temp workspace, snapshots old/new `go.mod`, computes dependency changes, emits main-module changelog, ensures changed dependency repos are available, appends dependency changelogs, builds stats JSON, prints a contributor table, and saves the GitHub handle cache.

## State And Persistence Behavior
It reads Git history across Kubo and dependency repos, may clone/fetch dependencies under `$GOPATH/src`, writes temporary JSON in a temp dir, and persists `~/.cache/mkreleaselog/github-handles.json` atomically.

## Dependencies And Integration Points
It depends on `git`, `go`, `jq`, optional authenticated `gh`, semver-ish Go module versions, `.mailmap`, and GitHub repository naming conventions.

## Risks And Test Signals
Risks include API rate limits, dependency repo fetch failures, fragile commit subject parsing, ignored-file pathspec mistakes, and cache corruption. Signals are a Markdown changelog, dependency sections, contributor table, and cache load/save diagnostics.
