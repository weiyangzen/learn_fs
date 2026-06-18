# sources/control-plane/rook/images/Makefile

Purpose: top-level image build entry for Rook images, currently delegating to the Ceph image build.

Important APIs/types/functions: includes `image.mk`, sets `PLATFORMS`, exports `TINI_VERSION`, defines pattern target `ceph.%`, `do.build`, `build.all`, and `help`.

Control flow: `make build` flows through `image.mk` to `do.build`, which builds `ceph.$(PLATFORM)`. `build.all` installs prerequisites and builds configured platforms by invoking the `ceph` subdirectory.

State and persistence: produces local container images and optional cache tags through `image.mk`.

Dependencies/integration: depends on GNU Make, Docker/Podman command variables from common make files, and `images/ceph/Makefile`.

Risks: platform matrix is limited to amd64/arm64 and target behavior depends heavily on included make variables.

Test signals: `make -C images help`, `make -C images BUILD_CONTAINER_IMAGE=false`, and platform-specific image target dry runs.
