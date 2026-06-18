<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/transfer_test.go -->
# sources/cloud-native/containerd/integration/client/transfer_test.go

## Purpose
Tests the generic transfer service with a simple import-stream to export-stream echo path for empty, small, and large byte payloads.

## APIs, Types, And Functions
The file defines `TestTransferEcho`, `newImportExportEcho`, `WriteBytesCloser`, `newWaitBuffer`, `waitBuffer.Close`, `waitBuffer.Bytes`, and `displayBytes`. It uses `client.Transfer`, `archive.NewImageImportStream`, and `archive.NewImageExportStream`.

## Control Flow And State
Each subtest creates a wait buffer, transfers bytes from an import stream to an export stream, waits for the export stream to close before reading `Bytes`, and compares output with the expected input. `displayBytes` truncates large diagnostic output in failure messages.

## Persistence And Integration Points
The test does not intentionally persist image metadata; it validates stream plumbing through the containerd transfer service and archive stream adapters. The only state is the in-memory buffer and close channel.

## Risks And Test Signals
Failures indicate transfer stream corruption, close ordering bugs, or incorrect handling of zero-length and larger payloads. The wait buffer prevents reading before the async export side has closed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/transfer_test.go -->
