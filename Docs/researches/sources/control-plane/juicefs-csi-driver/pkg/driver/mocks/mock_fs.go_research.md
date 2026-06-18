# sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_fs.go

Purpose: provides small fake `os.FileInfo` implementations for filesystem-related tests.

Important APIs and types: `FakeFileInfoIno1` and `FakeFileInfoIno2` implement `Name`, `Size`, `Mode`, `ModTime`, `IsDir`, and `Sys`. Their `Sys` methods return `*syscall.Stat_t` values with distinct inode numbers 1 and 2. `FakeFileInfoIno1` returns permissive mode; `FakeFileInfoIno2` returns device mode.

Control flow: there is no control flow beyond returning fixed values from interface methods.

State and persistence behavior: no state is stored or mutated. Values are synthetic and deterministic.

Dependencies and integration points: used by tests that patch `os.Stat` and need inode/mode-like data without touching real files. Depends on `io/fs`, `syscall`, and `time`.

Risks and test signals: because these fakes return minimal metadata, they can mask behavior that depends on real ownership, permissions, timestamps, directories, or non-Unix `Sys` values. They are test fixtures only.
