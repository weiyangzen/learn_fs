# sources/distributed-fs/ipfs-kubo/.github/workflows/sync-release-assets.yml

## Purpose
This workflow syncs missing binary release assets from `dist.ipfs.tech` into the latest GitHub releases.

## Important APIs, Types, And Functions
It starts an IPFS daemon via `ipfs/start-ipfs-daemon-action`, uses `actions/github-script` to call `github.rest.repos.listReleases` and `uploadReleaseAsset`, runs `ipfs ls/get` against `/ipns/dist.ipfs.tech/kubo/<tag>`, and verifies downloaded files with `sha512sum`.

## Control Flow
For up to five recent releases, it compares GitHub asset names to dist assets, skips files lacking both `.sha512` and `.cid` companions, downloads missing triples, validates checksums, and uploads the file plus checksum sidecars to the GitHub release.

## State And Persistence Behavior
State includes local downloaded artifacts, release asset lists, IPFS daemon repo state, and GitHub release assets. Successful runs persist uploaded assets to GitHub.

## Dependencies And Integration Points
It integrates GitHub Releases, IPNS resolution for `dist.ipfs.tech`, Kubo distribution naming, checksum conventions, and Node/GitHub Script APIs.

## Risks And Test Signals
Risks include IPNS/network unavailability, asset parsing assumptions around `ipfs ls`, off-by-one sync count behavior, and partial uploads. Signals are checksum success and uploaded assets appearing on recent releases.
