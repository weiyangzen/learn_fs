# Research: sources/cloud-native/buildkit/examples/buildkit1/buildkit.go

Purpose: second LLB example that refactors source checkout and copy behavior into reusable `StateOption` helpers while building a BuildKit image.

Important APIs and flow: `goFromGit` clones a repository into a temporary Alpine/git state, checks out a tag/ref, copies `/go` into the destination Go build state, and asynchronously sets the working directory to the copied repo. `copyFrom` composes copy behavior as a state option. `runc`, `containerd`, and `buildkit` use these helpers to build binaries and assemble an Alpine image. `main` marshals the graph to stdout after a debug listing run.

State and dependencies: output is LLB only; solve-time state pulls images and Git repositories. Depends on LLB async state options, Git, Go build images, and fs copy via `cp`.

Risks and test signals: async `GetDir`/`Reset` usage is more advanced and could be confusing or fragile if LLB APIs change. No direct tests are included.
