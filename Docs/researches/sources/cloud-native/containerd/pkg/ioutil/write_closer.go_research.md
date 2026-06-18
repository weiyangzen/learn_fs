# sources/cloud-native/containerd/pkg/ioutil/write_closer.go

Purpose: small write closer utilities: close notification, no-op close wrapping, and serialized concurrent writes.

Important APIs/types/functions: `NewWriteCloseInformer` wraps an `io.WriteCloser` and returns both the wrapper and a close channel that closes after `Close`. `NewNopWriteCloser` adapts an `io.Writer` to `io.WriteCloser` with no-op close. `NewSerialWriteCloser` wraps a write closer with a mutex around both `Write` and `Close`.

Control flow: wrappers delegate writes to the underlying writer. `writeCloseInformer.Close` calls the underlying close then closes the notification channel. `serialWriteCloser` serializes every write and close call, preventing interleaved concurrent writes for pipes and older kernel/file behavior.

State/persistence: in-memory wrapper state and one mutex/channel. Persistence depends on the underlying writer.

Dependencies/integration: generic package helper used where containerd needs close observation or atomic write groups.

Risks: `writeCloseInformer.Close` will panic if called twice because it closes the channel unguarded. `serialWriteCloser` cannot make partial writes atomic if the underlying writer itself returns short writes. Close waits behind active writes.

Test signals: `write_closer_test.go` validates close notification and non-interleaving under concurrent file writes.
