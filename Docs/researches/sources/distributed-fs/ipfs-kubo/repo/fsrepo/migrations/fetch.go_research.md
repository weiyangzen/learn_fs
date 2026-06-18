# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch.go

Purpose: downloads and unpacks external migration or Kubo binaries from an IPFS distribution path.

Important APIs and control flow: `FetchBinary` determines archive and binary names, rejects existing output files, creates or uses a download directory, chooses tar.gz or zip by OS, fetches archive bytes through a `Fetcher`, writes the archive, unpacks the requested binary, chmods it executable, and returns the output path. `osWithVariant` detects Linux musl via `ldd --version`. `makeArchivePath` builds distro/version/archive paths.

State and persistence: writes downloaded archives to temp or configured `DownloadDirectory`, writes extracted binaries, and sets executable mode.

Dependencies and integration: used by legacy migration downloads in `fetchMigrations`; depends on `Fetcher`, archive unpack helpers, runtime GOOS/GOARCH, and system `ldd`.

Risks and test signals: archive bytes are fully buffered by fetchers and then copied to disk. Existing output is a hard error. Tests cover fetch success, output collisions, permission/temp errors, bad dist, missing binary, dist env, and HTTP user agent/failover paths.
