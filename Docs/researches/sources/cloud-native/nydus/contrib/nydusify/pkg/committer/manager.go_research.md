# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager.go

Purpose: provides containerd operations needed by the committer: pause, resume, and inspect.

Important APIs and flow: `InspectResult` contains lowerdirs, upperdir, source image name, OCI mounts, and task PID. `NewManager` stores the containerd address. `Pause` and `UnPause` create a containerd client, load a container, get its task, and call `Pause`/`Resume`. `Inspect` loads the container, reads image name and task PID, unmarshals OCI spec mounts, queries the `nydus` snapshot service for snapshot mounts, requires at least one mount, and parses `lowerdir`/`upperdir` from mount options. `parseMountOptions` accepts arbitrary option order but requires both fields.

State and persistence: reads containerd metadata and controls task state. It creates new clients per call and does not close them explicitly.

Dependencies and integration: used by `Committer.Commit`, `syncFilesystem`, and pause handling. Assumes the snapshotter name is `nydus`.

Risks and test signals: missing client close can leak resources in long-running processes. Snapshotter name is hard-coded. It only uses the first returned mount. Mount option parsing is simple and does not unescape commas/colons.
