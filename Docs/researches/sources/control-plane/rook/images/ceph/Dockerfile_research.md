# sources/control-plane/rook/images/ceph/Dockerfile

Purpose: builds the Rook Ceph operator/toolbox image on top of a substituted Ceph base image.

Important APIs/types/functions: `FROM BASEIMAGE`, build args `S5CMD_VERSION` and `S5CMD_ARCH`, installs `iproute`, downloads `s5cmd`, copies `rook`, `toolbox.sh`, `set-ceph-debug-level`, monitoring files, and external cluster scripts, creates user `rook` UID 2016, sets entrypoint `/usr/local/bin/rook`.

Control flow: the Makefile copies artifacts into a temporary context and rewrites `BASEIMAGE` before Docker build.

State and persistence: image layers contain Rook binary, scripts, monitoring manifests, and helper tools.

Dependencies/integration: depends on Ceph base image, dnf repositories, GitHub s5cmd release, and built Rook binary.

Risks: network downloads during build reduce reproducibility; `dnf install` can fail when base repos are unavailable.

Test signals: image builds for both architectures and `rook`, `toolbox.sh`, `s5cmd`, and `ip` exist in the image.
