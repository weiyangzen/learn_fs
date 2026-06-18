# sources/distributed-fs/ipfs-kubo/bin/archive-branches.sh

## Purpose
This maintenance script moves inactive branches from the main GitHub repo to an archive repository and deletes them from origin after confirmation.

## Important APIs, Types, And Functions
Functions include `gh_api_next` for paginated GitHub API responses, `gh_api`, `pr_branches`, `origin_refs`, and `active_branches`. It uses `curl`, `jq`, `git for-each-ref`, `awk`, `comm`, and `git push`.

## Control Flow
The script adds an `archived` remote, computes branches that are neither active within the last month nor attached to PRs nor excluded, prints them, requires a yes confirmation, pushes each branch to the archive under a date suffix, then deletes the origin branch.

## State And Persistence Behavior
It mutates Git remotes by adding `archived`, creating archive refs, and deleting branches from origin.

## Dependencies And Integration Points
It integrates GitHub REST API, local remote-tracking refs, and SSH access to `ipfs/go-ipfs-archived`.

## Risks And Test Signals
Risks are high because it deletes branches, assumes old repo names, and relies on correct API pagination/filtering. Signals are the printed branch list and successful archive push before origin delete.
