## sources/cloud-native/overlaybd/src/test/image_service_test.cpp

Purpose: integration tests for image service acceleration/failover, metrics exporter, HTTP user-agent handling, dev-id registration, snapshot HTTP endpoint behavior, and snapshot creation.

Important helpers/tests: `new_server` starts a Photon TCP server. `AccelerateURL` checks p2p accelerate URL reachability. `failover` and `enableMetrics` exercise remote filesystem selection and metrics endpoint behavior. `http_client.user_agent` verifies Photon HTTP client user-agent propagation. `DevIDRegisterTest` sets up config files and image service state; `register_dev_id` checks image-file lookup and duplicate handling. `HTTPServerTest.http_server` probes `/snapshot` request validation. `CreateSnapshotTest` creates LSMT upper files and verifies snapshot data equivalence, sparse mode, and failure cases.

Control flow: tests write JSON configs into `/tmp/overlaybd`, create `ImageService`, create image files from config, perform reads/writes via aligned vectors, and delete resources. Several tests bind fixed local ports (`64208`, `64210`, `9862`, `9863`, `18731`) and rely on service startup side effects.

State/persistence: uses `/tmp/overlaybd`, `/var/log`, local LSMT data/index files, and localhost servers. Dependencies include Photon HTTP/socket/curl, GTest, image service implementation included directly, image file/LSMT, RapidJSON via build, and local filesystem.

Integration points: high-level regression suite for config parsing, p2p acceleration fallback, exporter behavior, service HTTP API, and snapshot layering. Risks: direct `system("echo ...")` JSON setup is shell-sensitive; hardcoded ports and `/opt/overlaybd/baselayers/ext4_64` fixture make tests environment-dependent; direct inclusion of `.cpp` can hide linkage issues. Test signal is valuable for end-to-end behavior but less hermetic.
