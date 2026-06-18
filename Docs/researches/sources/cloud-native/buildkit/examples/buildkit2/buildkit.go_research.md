# Research: sources/cloud-native/buildkit/examples/buildkit2/buildkit.go

Purpose: third LLB example that uses `llb.Git` directly as mounted source input instead of shelling out to git clone. It demonstrates cleaner source mounting and scratch output directories.

Important APIs and flow: `goRepo` returns a runner function that sets the working directory, mounts `llb.Git(repo, ref, options...)` at the repo path, and mounts a scratch `bin` directory for outputs. `runc`, `containerd`, and `buildkit` compile into repo-local `bin`. `copyAll` and `copyFrom` copy output trees into an Alpine result using the cp helper. `main` marshals a debug-listing state to stdout.

State and dependencies: no local persistence; solve-time fetches images and Git refs. Depends on LLB Git source operations, run mounts, and Go build commands.

Risks and test signals: remote refs and command paths are hard-coded and example-oriented. Containerd path uses module-style repo path and `KeepGitDir`. There are no direct tests.
