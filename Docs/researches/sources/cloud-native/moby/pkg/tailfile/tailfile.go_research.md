# sources/cloud-native/moby/pkg/tailfile/tailfile.go

Purpose: efficient reverse tailing for files or `SizeReaderAt` readers.

APIs and flow: `TailFile` builds a section reader over the file and scans returned tail content into byte slices. `NewTailReaderWithDelimiter` validates line count/delimiter, scans backward in 1 KiB blocks for delimiters, and returns a scoped `io.SectionReader` plus found line count. The internal scanner handles multi-byte delimiter overlap by rereading a small prefix.

State and dependencies: stateless aside from scanner position/buffer; uses `context` cancellation and `ReaderAt` reads.

Integration points: supports custom delimiters for logs beyond newline. `SizeReaderAt` matches `strings.Reader` and section readers.

Risks and tests: scanner returns borrowed scanner bytes in `TailFile`; callers should consume before next scan. Very long tokens are subject to bufio.Scanner limits. Tests cover empty files, truncated lines, delimiters, and block boundaries.
