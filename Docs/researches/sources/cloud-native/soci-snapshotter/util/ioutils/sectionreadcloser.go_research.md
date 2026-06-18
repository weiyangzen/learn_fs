# sources/cloud-native/soci-snapshotter/util/ioutils/sectionreadcloser.go

Purpose: this file adapts an `io.SectionReader` plus separate closer into a closeable section reader.

Important API: `SectionReadCloser` embeds `*io.SectionReader` and stores an `io.Closer`. `NewSectionReadCloser` constructs the pair. `Close` delegates to the stored closer.

Control flow: all read/seek/read-at behavior comes from the embedded `SectionReader`; close only affects the external closer, usually the underlying file or content reader.

State and persistence: no own persistence. Closing releases the resource represented by `c`.

Dependencies and integration points: useful for APIs that need an `io.ReadCloser` over a bounded section while retaining section-reader capabilities.

Risks: nil reader or closer will panic on use/close. Closing does not prevent further reads at this wrapper level if the underlying section reader still works. There are no direct tests in this subset.

Test signals: absent; recommended tests would cover read bounds and close delegation.
