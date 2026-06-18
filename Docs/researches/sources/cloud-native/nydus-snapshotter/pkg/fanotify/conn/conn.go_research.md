# Research: sources/cloud-native/nydus-snapshotter/pkg/fanotify/conn/conn.go

This file defines the small line-oriented client used by the fanotify server wrapper. `Client` owns a `bufio.Reader`, and `EventInfo` models newline-delimited JSON events with `path`, `size`, and `elapsed` fields. `GetEventInfo` reads until `\n`, unmarshals one event, and returns it.

There is no persistence here; the stream is owned by the fanotify process stdout pipe created in `pkg/fanotify/fanotify.go`. This package is intentionally minimal so the higher-level receiver can convert events to plain text and CSV. Dependencies are limited to `bufio` and `encoding/json`.

Risks include assuming each event is newline-delimited JSON, returning read errors directly, and allocating one full line in memory. Partial or malformed JSON terminates the receiver. The `Size` field is `uint32`, so very large values would truncate if the producer emits larger numbers. There are no direct tests for stream parsing or malformed input in this subset.
