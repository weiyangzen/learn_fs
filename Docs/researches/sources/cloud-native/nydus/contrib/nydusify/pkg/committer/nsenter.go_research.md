# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter.go

Purpose: builds and executes `nsenter` commands for running programs inside a target process namespace.

Important APIs and flow: `Config` contains booleans and optional namespace file paths for cgroup, IPC, mount, net, PID, user, and UTS namespaces, plus UID/GID, root, working directory, no-fork, credential preservation, SELinux context, and target PID. `Execute` uses a background context. `ExecuteContext` builds the base command, opens stdout pipe, appends program and args, captures stderr, starts the process, copies stdout to the supplied writer, and waits. `buildCommand` validates `Target`, appends `nsenter` flags for enabled fields, and returns `exec.CommandContext(ctx, "nsenter", args...)`.

State and persistence: runs external processes and streams their output. No persistent files are created by this wrapper.

Dependencies and integration: used by committer to run `sync` and `tar` in container mount/PID namespaces.

Risks and test signals: stdout pipe close is polled by a goroutine checking `ProcessState`, which may lag until `Wait`. Typo-compatible flag `--ip=<file>` is used for IPC file mode, matching current code but worth validating against util-linux `nsenter`. Requires host privileges and `nsenter` binary.
