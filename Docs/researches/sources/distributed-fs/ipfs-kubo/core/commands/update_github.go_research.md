# sources/distributed-fs/ipfs-kubo/core/commands/update_github.go

Purpose: implements GitHub Release discovery, asset download, checksum download, SHA-512 verification, and platform asset naming for `ipfs update`.

Important APIs/types/functions: `ghRelease`, `ghAsset`, `githubGet`, `githubToken`, `githubLatestRelease`, `githubListReleases`, `githubReleaseByTag`, `findReleaseAsset`, `downloadAsset`, `downloadAndVerifySHA512`, `verifySHA512`, and `assetNameForPlatformTag`.

Control flow: API calls use `githubReleaseBaseURL`, which can be overridden only through `TEST_KUBO_UPDATE_GITHUB_URL`. `githubGet` sets GitHub JSON accept headers, Kubo user agent, and optional bearer token, then maps 403/429 to rate-limit errors. Release listing over-fetches when prereleases are excluded. Latest release scans for a matching platform asset. Downloads stream through `io.LimitReader` capped at 200 MiB. Checksum verification downloads `archiveURL + ".sha512"`, parses the first field as hex, and compares to `sha512.Sum512(data)`.

State and persistence behavior: no durable state; all downloads are in-memory. Environment variables `GITHUB_TOKEN`/`GH_TOKEN` affect API auth, and test env var affects base URL.

Dependencies and integration points: used by `update.go`; depends on `net/http`, `runtime.GOOS/GOARCH`, Kubo current version for User-Agent, and GitHub release asset naming convention.

Risks: checksum sidecar is fetched from the same distribution origin as the archive, so it detects corruption but not compromise of release assets. No retry/backoff. `githubListReleases` can return fewer than requested if more than 3x prereleases appear before stable releases. Download limit protects memory but still reads full allowed payload into memory.

Test signals: `update_github_test.go` provides extensive unit coverage for headers, rate-limit errors, release filtering, asset lookup, download errors, checksum verification, archive extraction, and version helpers.
