<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_test.go -->
# sources/cloud-native/moby/client/container_logs_test.go

Purpose: validates log retrieval error handling, query encoding, timestamp parsing, and stream behavior.

Important coverage: not-found and internal errors, invalid empty/whitespace ids, invalid `Since`/`Until` parse errors, default suppression of `tail=all`, explicit tail values, stdout/stderr/follow/timestamps/details flags, and reading returned content.

Control flow and dependencies: table-driven tests inspect request queries and use mock bodies for stream reads.

State and risks: no persistence. The suite is high-signal for one of the common long-lived streaming client methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_test.go -->
