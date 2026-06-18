# sources/distributed-fs/ipfs-kubo/.github/workflows/interop.yml

## Purpose
This workflow tests Kubo interoperability with Helia and the IPFS WebUI.

## Important APIs, Types, And Functions
`interop-prep` builds `cmd/ipfs/ipfs` and uploads it as an artifact. `helia-interop` downloads the binary, installs the current `@helia/interop`, and runs `npx aegir test`. `ipfs-webui` checks out `ipfs/ipfs-webui`, installs Node dependencies and Playwright, builds the WebUI test app, and runs E2E tests with `IPFS_GO_EXEC`.

## Control Flow
Both interop jobs depend on the built Kubo artifact. Caches are keyed by npm package versions, lockfiles, Playwright browser metadata, and WebUI sources. A known Helia MFS CID mismatch test is excluded pending IPIP-499 alignment.

## State And Persistence Behavior
The workflow persists the Kubo binary artifact and caches Node modules, Playwright browsers, and WebUI build output. Failure artifacts include WebUI test results.

## Dependencies And Integration Points
It integrates Kubo's daemon/binary behavior with external JS IPFS implementations, Playwright/browser dependencies, GitHub commit status via `gh api`, and WebUI E2E configuration.

## Risks And Test Signals
Risks include latest `@helia/interop` drift, external repo instability, network/npm failures, and the explicit skip masking one compatibility gap. Signals are successful Helia Aegir tests and WebUI E2E tests against the local Kubo binary.
