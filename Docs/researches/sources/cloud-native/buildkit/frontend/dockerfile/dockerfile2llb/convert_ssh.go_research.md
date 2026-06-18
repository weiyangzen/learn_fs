# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_ssh.go

Purpose: converts SSH mounts for RUN into LLB SSH socket options and records outline metadata.

Important API: `dispatchSSH(d, m, loc)` returns `llb.AddSSHSocket(...)`.

Control flow: SSH mounts reject `source`. ID defaults to `default` for outline, while options use `m.CacheID`. Target, optional flag, and socket uid/gid/mode are appended when configured; default mode is `0600` if any file metadata is set.

State and persistence: records SSH id, required flag, and location in `dispatchState.outline.ssh`. No secret material is persisted.

Dependencies and integration: called by RUN mount dispatch and represented in outline subrequests.

Risks and test signals: possible risk is the option ID using `m.CacheID` instead of the local defaulted `id`; empty id likely means default to LLB, but this contract matters. SSH mount and outline tests are relevant.
