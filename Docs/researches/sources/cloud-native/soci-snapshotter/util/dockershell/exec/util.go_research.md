# sources/cloud-native/soci-snapshotter/util/dockershell/exec/util.go

Purpose: this file provides Docker utility helpers for temporary networks and temporary images used by integration tests.

Important APIs and types: `NewTempNetwork` creates a Docker network and returns a cleanup function. `Connect` attaches an `Exec` container to a network. Image options configure patch Dockerfile content, patch build context, build args, and build stdio. `NewTempImage` builds an image from a context and optional target stage, optionally then builds a derived patch image. `newTempImage` performs the actual Docker build and returns image tag plus cleanup.

Control flow: `NewTempImage` requires an absolute context dir. If a patch context is specified, a patch Dockerfile must also be specified. It first builds the base image; without patch content, it returns that image and cleanup. With patch content, it defers cleanup of the base image, creates or uses a patch context, writes a Dockerfile `FROM <base>` plus patch content, and builds a second image. `newTempImage` generates a unique tag, assembles `docker build -q -t`, optional Dockerfile, target, build args, and context, then returns cleanup that removes the image.

State and persistence: creates Docker networks/images and temporary Dockerfile/context directories. Cleanup removes created network/image and temporary directories created by the helper.

Dependencies and integration points: uses Docker CLI, xid, filesystem temp dirs, and `Exec` for container identity in `Connect`.

Risks: cleanup is caller-managed and setup failures can leak resources. Patch Dockerfile is written with mode `0666`, subject to umask, broader than needed. Temporary image names are not namespaced beyond `tmpimage<id>`. Build args are passed directly to Docker CLI.

Test signals: no direct tests in this subset; requires Docker integration coverage.
