# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/status_test.go

This test file validates sandbox status storage transactions and state string conversion. `TestStatus` creates an initial status with PID, creation time, and unknown state, stores it with `StoreStatus`, and confirms `Get` returns the same value. It then applies an update function returning an error and verifies the stored status remains unchanged. A successful update changes the in-memory status to a ready state with a new PID and creation time.

`TestStateStringConversion` verifies `StateReady`, `StateNotReady`, and `StateUnknown` string values, plus formatting for an invalid numeric state. This matters because server-side status conversion uses these strings to map to CRI enums, and unknown must remain distinguishable internally even though CRI maps it to not-ready.

The tests cover rollback and simple mutation but not concurrent updates, pointer resource aliasing, overhead/resource fields, stop-channel side effects, or integration with `PodSandboxStatus`. They also intentionally do not test checkpointing because sandbox status storage is in-memory only.
