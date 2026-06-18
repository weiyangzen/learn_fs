# sources/cloud-native/stargz-snapshotter/script/util/make.sh

Purpose: Runs repository `make` targets inside a minimal privileged Go container.
Important APIs/types/functions: uses `go_base_version`, generated Dockerfile, `MAKECMD=make ... PREFIX=/tmp/out/`.
Control flow: builds a `golang:<version>` image with fuse3/gzip/pigz, then runs the requested make target with the repo mounted read-only and git safe.directory configured.
State and persistence: creates a temp Docker build context and local image `minienv`; build outputs stay inside the container unless target writes elsewhere.
Dependencies and integration points: depends on Docker, Go base image, FUSE device, and repository Makefile.
Risks: repo is mounted read-only, so make targets that write to source will fail; command arguments are interpolated into `/bin/sh -c`.
Test signals: useful for reproducible build/test invocations in CI or developer scripts.
