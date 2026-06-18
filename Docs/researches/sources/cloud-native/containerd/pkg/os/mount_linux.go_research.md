# sources/cloud-native/containerd/pkg/os/mount_linux.go

Purpose: Linux `RealOS` mount operations.

Important APIs/types/functions: `RealOS.Mount` calls `mount.Mount`; `RealOS.Unmount` calls `mount.Unmount`; `RealOS.LookupMount` calls `mount.Lookup`.

Control flow: thin delegation from the OS abstraction to containerd's mount package.

State/persistence: affects host mount table when called. Lookup reads mount state.

Dependencies/integration: selected on Linux; implements the mount methods of `pkg/os.OS`. Used by code that wants an injectable OS interface for filesystem and mount operations.

Risks: mount/unmount require privileges and can affect host state. Errors are returned without wrapping, so callers need context.

Test signals: fake OS tests outside this list can validate call recording; integration tests should cover mount behavior on Linux with appropriate privileges.
