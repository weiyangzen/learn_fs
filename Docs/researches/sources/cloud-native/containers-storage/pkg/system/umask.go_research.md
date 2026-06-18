# sources/cloud-native/containers-storage/pkg/system/umask.go

Purpose: Unix wrapper for setting the process file mode creation mask.

Important APIs/types/functions: `Umask(newmask int) (oldmask int, err error)`.

Control flow: calls `unix.Umask(newmask)` and returns the previous mask with nil error.

State/persistence: changes process-global umask, affecting future file creation in the current process.

Dependencies/integration: used by CLI or storage setup paths that need controlled file permissions.

Risks: umask is process-global and not goroutine-local; changing it in concurrent programs can affect unrelated file creation.

Test signals: tests should save/restore the original mask and avoid parallel execution.
