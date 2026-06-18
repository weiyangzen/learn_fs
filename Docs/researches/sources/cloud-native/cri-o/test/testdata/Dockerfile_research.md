<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/Dockerfile -->
# sources/cloud-native/cri-o/test/testdata/Dockerfile

Purpose: builds the Fedora-based CRI-O CI image used by many runtime tests.

Important flow: starts from `quay.io/fedora/fedora-minimal:38`, installs basic tools, compiler, networking utilities, OpenSSL headers, process tools, and wget; creates a test user/group and adjusts `/etc` permissions; builds and installs `su-exec`; downloads and verifies Redis 6.0.18, builds it with TLS, installs it, and sets a Redis-style entrypoint, data volume, exposed port, and default command. It also declares `/imagevolume` for image-volume tests.

State and integration: produces `quay.io/crio/fedora-crio-ci:latest` variants used in CRI request fixtures and NRI runtime helpers. Risks include external download availability, Fedora package drift, Redis checksum/version updates, and architecture-specific build behavior. Test signal is image-dependent integration behavior rather than Dockerfile unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/Dockerfile -->
