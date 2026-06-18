## sources/cloud-native/moby/integration-cli/events_utils_test.go

Purpose: utility support for CLI event tests. It defines matcher/processor function types, `eventObserver` for long-running `docker events`, regex-style event parsing helpers, and event action filtering by ID/type.

Control flow: `newEventObserver` computes a daemon-relative `--since` timestamp, prepares an `exec.Cmd`, and attaches stdout to a scanner. `Start` launches it; `Match` scans lines, buffers them, and invokes a processor for matches. `CheckEventError` recovers from scanner disconnects by querying `docker events --since/--until`. Matching uses `eventstestutils.ScanMap` and can resolve IDs through event attributes.

State includes the observer buffer, command process, scanner error, and channels closed or signaled by `processEventMatch`. Dependencies include daemon time helpers, Docker CLI, containerd logging, and event test utilities. Risks are event stream disconnections, race windows around since/until, and simple comma/equals parsing of attributes. Test signals are observed action channels, fatal diagnostics with buffered output, and parsed action lists.
