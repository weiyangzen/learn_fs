# sources/compression/zstd/contrib/docker/Dockerfile

Purpose: multi-stage Dockerfile producing a minimal Alpine image containing installed zstd binaries/libraries.

Important behavior: the builder stage uses a pinned Alpine image digest, installs `make gcc libc-dev`, copies the repository to `/src`, runs `make`, and installs into `/pkg` via `make DESTDIR=/pkg install`. The final stage uses the same pinned Alpine digest, copies `/pkg` into the image, creates a license directory, copies `LICENSE`, and defaults `CMD` to `/usr/local/bin/zstd`.

State, dependencies, and integration: build state is confined to Docker layers. It integrates the top-level make/install path with Alpine/musl packaging expectations.

Risks and test signals: the final `COPY` path uses `/usr/local/share/licences/zstd/` while the directory created is `/usr/local/share/licenses/zstd`, a spelling mismatch that can place the license under an unintended directory. The image does not run tests; successful build/install is the signal.
