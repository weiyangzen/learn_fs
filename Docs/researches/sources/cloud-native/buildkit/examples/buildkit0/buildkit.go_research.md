# Research: sources/cloud-native/buildkit/examples/buildkit0/buildkit.go

Purpose: first LLB example for constructing a BuildKit image from source using imperative copy helper patterns. It writes the resulting LLB definition to stdout.

Important APIs and flow: flags choose whether to include containerd plus runc/containerd versions. `goBuildBase` builds a Go Alpine state with build dependencies. `runc` and `containerd` clone upstream repos, checkout versions, and compile binaries. `buildkit` clones BuildKit, builds `buildkitd` and `buildctl`, starts from Alpine, copies binaries and optionally containerd in. `copy` uses an Alpine `cp -a` run with source/destination mounts. `main` marshals the final state after a debug `ls -l /bin` run.

State and dependencies: no local persistence except stdout LLB; build state references remote Git repos and images when solved. Depends on LLB DSL and system path helpers.

Risks and test signals: it is an example with hard-coded versions and remote repositories. The cp-based copy helper is less idiomatic than later examples. No direct tests are present.
