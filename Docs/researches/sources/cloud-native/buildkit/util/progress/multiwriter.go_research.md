## sources/cloud-native/buildkit/util/progress/multiwriter.go

Purpose: aggregates progress writes and replays sorted history to newly attached writers.

Important APIs/types: `MultiWriter`, `NewMultiWriter`, `Add`, `Delete`, `Write`, `WriteRawProgress`, `Close`, and cycle-detection helper `contains`.

Control flow: `Write` creates a timestamped `Progress` with shared metadata, stores it, and forwards to attached raw writers. `Add` accepts only writers implementing raw progress, detects `MultiWriter` cycles and panics on loops, sorts existing items by timestamp, replays them, and registers writer. `WriteRawProgress` decorates incoming progress with metadata without overwriting existing metadata.

State/persistence: in-memory history, writer set, metadata map protected by mutex. Dependencies: `slices`, `sync`, time.

Integration points: progress fan-in/fan-out for solver and flightcontrol. Risks: unbounded history; `Close` is no-op so attached writers are not closed; writing while holding lock means a slow writer blocks all writes and may deadlock if it calls back. Test signals: no direct tests in this subset.
