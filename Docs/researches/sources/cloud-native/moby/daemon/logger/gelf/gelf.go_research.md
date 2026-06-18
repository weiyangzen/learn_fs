## sources/cloud-native/moby/daemon/logger/gelf/gelf.go

Purpose: Implements the GELF log driver for Graylog-compatible endpoints over UDP or TCP, including address validation, UDP compression options, TCP reconnect options, metadata enrichment, and message emission.

Important APIs and types: `gelfLogger` stores a GELF writer, logger info, hostname, and pre-marshaled extra metadata. `New`, `newGELFTCPWriter`, `newGELFUDPWriter`, `Log`, `Close`, `Name`, `ValidateLogOpt`, and `parseAddress` form the driver.

Control flow and state: `New` requires `gelf-address`, resolves host metadata, parses tag, builds `_container_id`, `_container_name`, `_image_id`, `_image_name`, `_command`, `_tag`, `_created`, and extra attributes prefixed with `_`, marshals them once, then constructs a UDP or TCP writer. UDP supports compression type (`gzip`, `zlib`, `none`) and level. TCP supports max reconnect and reconnect delay. `Log` ignores empty lines, maps stderr to GELF error level, converts timestamp to fractional seconds, includes raw extras, writes through the GELF writer, and returns the message to the pool on success.

Dependencies and integration points: Uses `Graylog2/go-gelf`, logger tag and extra attribute helpers, hostname lookup, JSON metadata, and Docker logger factory registration.

Risks: `New` has a default branch that would return a logger with nil writer for unsupported schemes, but `parseAddress` prevents unsupported schemes before the switch. TCP reconnect delay is parsed as an integer and assigned directly as `time.Duration`, so the unit is nanoseconds unless the upstream writer interprets it differently. Metadata is pre-marshaled, so per-message dynamic metadata is not supported.

Test signals: `gelf_test.go` covers address parsing, TCP/UDP option validation, writer construction, and logger construction for both protocols on Linux.
