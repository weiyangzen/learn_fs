# sources/distributed-fs/ceph-client/tools/perf/perf-archive.sh

### Purpose
`perf-archive.sh` packages or unpacks build-id debug symbol files needed to analyze a `perf.data` file on another machine. With `--all` it also bundles `perf.data`.

### Important APIs, Types, And Functions
The script parses `--all`, `--unpack`, `--exclude-buildids`, and an optional perf.data or archive path. It uses `perf buildid-list -i <data> --with-hits` to collect build ids, constructs a tar manifest from `.build-id` links and resolved debug files, and creates bzip2 tar archives.

### Control Flow
Unpack mode locates or validates an archive, distinguishes `perf.all*.tar.bz2` bundles from symbol-only archives, prompts before overwriting current-directory files, then extracts symbols into `~/.debug`. Pack mode resolves `PERF_BUILDID_DIR` or defaults to `~/.debug`, builds a temporary build-id list with optional exclusions, generates a manifest, and writes either `perf.data.tar.bz2` or `perf.all-<host>-<date>.tar.bz2`.

### State And Persistence
Persistent outputs are tarballs and extracted files under `~/.debug`. Temporary build-id and manifest files are created under `/tmp` and normally removed. Existing unpack targets can be overwritten after prompting.

### Dependencies And Integration Points
It depends on Bash, `perf`, `tar`, `grep`, `comm`, `readlink`, `mktemp`, `hostname`, `date`, and the perf build-id cache layout.

### Risks
Several variable expansions are unquoted in pack paths, so paths with spaces are risky. Unpack auto-discovery errors when multiple matching archives exist. Exclusion semantics require a correctly formatted build-id list.

### Test Signals
Create archives from perf.data with and without `--all`, apply an exclusion list, unpack into a clean home/debug directory, and verify `perf report` resolves symbols from the archive.
