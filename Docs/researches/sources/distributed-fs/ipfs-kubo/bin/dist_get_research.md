# sources/distributed-fs/ipfs-kubo/bin/dist_get

## Purpose
This portable shell script downloads and extracts a named binary distribution from the IPFS distribution site for the current or specified Go platform.

## Important APIs, Types, And Functions
Functions include `die`, `have_binary`, `check_writable`, `try_download`, `download`, `unarchive`, `get_go_vars`, and `mkurl`. It supports `wget`, `curl`, `fetch`, `http`, `ftp`, `tar`, and `unzip`.

## Control Flow
The script validates `<distroot> <distname> <outpath> <version>`, requires `v*` versions, determines `GOOS-GOARCH`, selects `tar.gz` or `zip`, downloads to `bin/tmp`, extracts the binary named after the distribution, and chmods it executable.

## State And Persistence Behavior
It writes archives into `bin/tmp` and the extracted executable to `outpath`, including `.exe` suffix on Msys/Cygwin.

## Dependencies And Integration Points
It integrates Make helper downloads, Go environment detection, and `https://ipfs.io` distribution URL layout.

## Risks And Test Signals
Risks include `eval`-based downloader commands, dependency on Go for platform detection, unsupported OS strings, and no checksum verification. Signals are a downloaded archive and executable output file.
