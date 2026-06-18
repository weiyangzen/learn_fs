## sources/cloud-native/buildkit/util/iohelper/helper.go

Purpose: small IO adapter utilities for closing composition, write counting, and ReaderAt-to-ReadCloser conversion.

Important APIs/types: `NopWriteCloser`, `WithCloser(r, closer)`, `WriteCloser{io.WriteCloser, CloseFunc}`, `Counter`, `ReaderAtCloser`, and `ReadCloser(in)`.

Control flow: composed closers call the wrapped closer first and the additional close func second, returning wrapped first error with second error embedded in message or returning the second error. `Counter.Write` increments byte count under mutex and reports full write. `ReadCloser` wraps a `ReaderAtCloser` in a section reader over `Size`.

State/persistence: `Counter` keeps in-memory count protected by mutex. Dependencies: standard `io`, `sync`, `pkg/errors`.

Integration points: content streaming, progress/log counting, wrappers around content `ReaderAt`. Risks: `WithCloser` and `WriteCloser.Close` always invoke both closers but only preserve first error structurally; `ReadCloser` assumes stable `Size()` and random access. Test signals: no local tests in this subset.
