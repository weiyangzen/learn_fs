# sources/cloud-native/moby/pkg/tailfile/tailfile_test.go

Purpose: broad correctness and benchmark coverage for reverse tailing.

APIs and flow: file-level tests cover last-N lines, requesting more lines than present, empty file, and invalid counts. `TestNewTailReader` runs parallel table tests over newline and multi-byte delimiters, varied line sizes, JSON-like log lines, empty data, and truncated final lines.

State and dependencies: uses temp files and in-memory `strings.Reader` values; no persistent state.

Integration points: confirms `TailFile` and `NewTailReaderWithDelimiter` agree with normal forward reads.

Risks and signals: validates page/block crossing behavior and page-size-like large lower inputs. Benchmark measures 10k-line tail performance.
