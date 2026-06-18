# sources/cloud-native/moby/daemon/logger/journald/internal/fake/sender.go

Purpose: test-only journald sender that creates real journal files without depending on a running journald daemon.

Important APIs/types/functions: `JournalRemoteCmdPath` locates `systemd-journal-remote`; `New` and `NewT` construct `Sender`; `Sender.Send` mirrors `journal.Send`. `ErrCommandNotFound` lets tests skip cleanly. `Sender` stores command path, output journal file, optional time source, boot ID, test helper, and event timestamp mode.

Control flow/state/persistence: `Send` builds one export-format entry with required `__REALTIME_TIMESTAMP`, `_BOOT_ID`, `MESSAGE`, `PRIORITY`, and validated user vars, then invokes `systemd-journal-remote --output <file> -`. Each call starts a process so return implies flush to disk.

Dependencies/integration: uses `export.WriteField`, `go-systemd/journal`, UUIDs, lazy regexp, and external systemd tooling. Journald read tests inject this sender into the driver.

Risks: environment-sensitive: tests require `systemd-journal-remote` and journal format compatibility. Invalid variable names are rejected; timestamp parsing can fail in synthetic mode.

Test signals: used by journald read tests to create deterministic journal files and verify reader behavior.
