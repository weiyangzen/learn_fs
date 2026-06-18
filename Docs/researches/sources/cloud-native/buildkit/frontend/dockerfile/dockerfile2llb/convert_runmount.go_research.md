# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runmount.go

Purpose: converts `RUN --mount` options into LLB run mount options and records mount source dependencies/paths.

Important APIs: `detectRunMount` records dependency states for mounts; `setCacheUIDGID` prepares cache mount ownership/mode; `dispatchRunMounts` returns `[]llb.RunOption`.

Control flow: mount sources are resolved to existing stages or unregistered external sources; cache mounts without `from` use scratch/empty image source. Tmpfs, secret, and SSH mounts dispatch to special handlers. Bind mounts can be readonly or forced no-output for rw bind without cap support. Cache mounts map sharing mode and persistent cache ID with namespace. Relative targets are resolved under current workdir; `/` target is rejected. Source paths are recorded against build context or source stage for path filtering.

State and persistence: persistent cache mounts use `AsPersistentCacheDir`; stage/context path maps mutate `dispatchState` for later local filtering. Secret/SSH outline state is mutated by sub-handlers.

Dependencies and integration: used by RUN dispatch; integrates Dockerfile mount parser, LLB mount options, solver caps, system path helpers, and secret/SSH handlers.

Risks and test signals: risks include dependency ordering, relative target resolution, source path accounting, cache permission setup, and cap-dependent bind behavior. RUN mount integration tests cover this surface.
