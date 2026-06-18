# sources/distributed-fs/ipfs-kubo/test/cli/ipfswatch_test.go

Purpose: tests the `ipfswatch` command-line tool on platforms with fsnotify support, including basic file ingestion and datastore plugin loading.

Important APIs/functions: `TestIPFSWatch` builds `cmd/ipfswatch/ipfswatch` if absent, starts it via `Runner.Run` with `RunFuncStart`, watches a temp directory, and validates emitted CIDs. It also mutates datastore config for pebbleds.

Control flow: before parallel subtests, the binary is built once. The first subtest starts ipfswatch, waits for initialization, writes a unique file, polls stderr for `added ... key: CID`, stops the watcher to release the repo lock, then reads content with `ipfs cat --offline`. The second configures pebbleds as the root datastore and checks startup stderr for plugin errors.

State and persistence: builds a binary under the repo, modifies node repo config/datastore directory, creates watched files, and adds content to the repo.

Dependencies/integration: depends on fsnotify, Go build, Kubo datastore plugins, pebbleds support, regex parsing, and process cleanup.

Risks: fixed sleeps and stderr log parsing are timing-sensitive. Killing background processes must release repo locks. Test signals are absence of “unknown datastore type,” captured CID, successful offline cat, and exact content match.
