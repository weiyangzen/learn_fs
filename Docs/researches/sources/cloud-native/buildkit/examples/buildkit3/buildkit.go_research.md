# Research: sources/cloud-native/buildkit/examples/buildkit3/buildkit.go

Purpose: fourth LLB example that adds local-source support and uses native `llb.Copy` file operations instead of shell-based copy runs. It builds a scratch image containing BuildKit, runc, and optional containerd binaries.

Important APIs and flow: flags include buildkit/containerd/runc versions, with `"local"` selecting `llb.Local` sources. `goRepo` mounts the chosen source read-only and a scratch `/out`. `runc`, `containerd`, and `buildkit` compile binaries to `/out`. `buildkit` assembles a scratch state with `copyAll`. `copy` uses `dest.File(llb.Copy(..., AllowWildcard, AttemptUnpack, CreateDestPath))`, showing modern LLB copy semantics. `main` marshals the final state to stdout.

State and dependencies: output is serialized LLB; solve-time state may read local named contexts (`runc-src`, `containerd-src`, `buildkit-src`) or remote Git. Depends on LLB file operations and system path helper.

Risks and test signals: local source names must be provided by the solve client when using `"local"`. This example is not unit-tested, but it demonstrates a safer copy primitive than prior examples.
