# sources/cloud-native/nydus-snapshotter/pkg/converter/utils.go

Purpose: provides utility types and functions for tar packaging and content-store JSON read/write operations used by converter hooks.

Important APIs and functions: `File`; `writeCloser` and `newWriteCloser`; `seekReader`; `newSeekReader`; `packToTar`; `readJSON`; and `writeJSON`.

Control flow: `writeCloser.Close` closes the underlying writer once and then runs an action callback, making converter pack writers finish background conversion on close. `seekReader` adapts an `io.ReaderAt` to sequential read/seek operations for tar parsing. `packToTar` streams an `image/` directory and supplied files into tar or tar.gz through an `io.Pipe`. `readJSON` reads descriptor labels and JSON content from a content store. `writeJSON` marshals JSON, computes digest, opens a content writer with a deterministic ref, copies data with labels, closes it, and returns an updated descriptor.

State and persistence: `packToTar` uses goroutine/pipe state only. `writeJSON` persists new JSON blobs into the content store and preserves supplied labels. `writeCloser` tracks close state.

Dependencies and integration points: used throughout manifest/config rewrite paths in `convert_unix.go` and `reconvert_unix.go`.

Risks: `seekReader.Seek` does not support `io.SeekEnd` and does not bounds-check negative positions. `packToTar` uses `filepath.Join` for tar entry names; on Windows this could emit backslashes, though converter Unix paths use it. `writeJSON` does not explicitly handle already-existing content beyond whatever `content.Copy` does.

Test signals: no direct tests in listed files; many converter tests indirectly rely on `readJSON`.
