# sources/control-plane/mayastor/test/python/v1/rebuild/docker-compose.yml

Purpose: single-node v1 rebuild test environment. It launches `ms0` at `10.1.0.2`.

Important configuration: command runs io-engine with cores `1,2` and `/tmp/ms0.sock`. Environment enables ANA and reservations, sets PATH and ASAN leak suppression, and uses the standard source, `/nix`, hugepages, `/tmp`, and `/var/tmp` mounts. Capabilities and unconfined seccomp are granted for SPDK/io-engine.

State and integration: rebuild tests create aio files in host `/tmp`, which are visible to the container. Python v1 fixtures connect to the service over `mayastor_net` and call the v1 nexus rebuild RPCs.

Risks and test signals: only one node is present, so tests focus on local file-backed children and rebuild state transitions rather than network failures. Environment failures show up as gRPC readiness or file access failures. Assertions live in the paired rebuild tests.
