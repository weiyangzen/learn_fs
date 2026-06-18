# Research: sources/cloud-native/buildkit/examples/build-using-dockerfile/main.go

Purpose: example CLI that mimics a small subset of `docker build` by using BuildKit to build a Dockerfile and load the result into Docker. It is explicitly not a production replacement.

Important APIs and flow: `main` defines flags for build args, Dockerfile path, tag, target, no-cache, BuildKit address, and optional client-side frontend. `action` requires a tag, creates a BuildKit client, builds a `SolveOpt`, runs either `client.Build` with client-side Dockerfile frontend or daemon `Solve`, displays progress, and pipes docker exporter output to `docker load`. `newSolveOpt` maps context and Dockerfile directories to fsutil local mounts, sets frontend attrs, build args, no-cache, and docker exporter output writer. `loadDockerTar` shells out to `docker load`.

State and dependencies: reads local build context/Dockerfile, streams image tar, and mutates local Docker image store via `docker load`. Depends on BuildKit client, Dockerfile builder, fsutil, progress UI, errgroup, and external Docker CLI.

Risks and test signals: the example has limited flag compatibility and no stdin context support. External Docker and daemon availability are required. No direct tests are in this subset.
