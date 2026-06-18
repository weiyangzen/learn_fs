# sources/distributed-fs/beegfs-go/.github/workflows/no-todo-commits.yml

## Purpose
This GitHub Actions workflow prevents pull requests from merging commits whose first commit-message line contains TODO or WIP.

## Control Flow
On opened, synchronized, or reopened pull requests, an `actions/github-script@v7` step lists PR commits, extracts each commit message's first line, filters case-insensitively for word-boundary `TODO` and `WIP`, and fails the check with a formatted message if any are found.

## Dependencies and Integration
The workflow uses the GitHub REST pulls API through `github-script` and read-only repository permissions. It integrates as a PR status check.

## Risks and Test Signals
Only the first line is checked, so TODO/WIP in message bodies is allowed. The regex is word-boundary based and may flag intended words in commit prefixes. The failure message includes commit first lines but not SHAs, although the script records SHAs internally.
