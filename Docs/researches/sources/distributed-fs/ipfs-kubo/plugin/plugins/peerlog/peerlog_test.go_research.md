<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go

## Purpose

This file tests peerlog's config parser for the `Enabled` flag.

## Important APIs, Types, and Functions

`TestExtractEnabled` table-tests nil config, wrong config type, missing field, nil field, non-boolean field, and true boolean field.

## Control Flow, State, and Integration

The tests call `extractEnabled` directly and do not start a node or plugin.

## Dependencies, Risks, and Test Signals

Dependency is the testing package only. The test covers opt-in safety but not runtime event logging, queue overflow, or close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go -->
