# sources/cloud-native/nydus-snapshotter/cmd/optimizer-nri-plugin/main.go

Purpose: NRI plugin that starts/stops fanotify-based optimizer collection per container.

Flow: CLI sets plugin name/index/events and optimizer config. `Configure` optionally parses TOML runtime config and event mask. `StartContainer` derives repo/image tag from CRI image annotation, creates a persist dir, constructs a fanotify server for the container PID, starts it, and stores it by image name. `StopContainer` stops the matching server. `onClose` stops all servers.

State/dependencies: global config, syslog writer, and `globalFanotifyServer` map; persists accessed-file lists under configured directory.

Integration points: tested by optimizer workflow and `misc/example/optimizer-nri-plugin.conf`.

Risks/tests: map key is image name, so concurrent containers from the same image can overwrite each other. Type assertion to `NamedTagged` can panic if annotation lacks tag.
