# sources/control-plane/mayastor/io-engine/tests/wipe.rs

Purpose: v1 test-service integration test for streamed replica wipe progress, chunk validation, and write-zero data effects.

Important APIs/types/functions: `replica_wipe` drives scenarios through `issue_wipe_replica`, `collect_stream`, `validate_wipe_replica`, `wipe_replica`, `create_pool_replica`, and `nvme_device`. It uses `WipeMethod`, `WipeReplicaRequest`, `StreamWipeOptions`, `WipeReplicaResponse`, `NmveConnectGuard`, `dd_urandom_blkdev`, and `compare_devices`.

Control flow: a containerized io-engine creates a 1 GiB thick replica. Multiple `WipeMethod::None` cases validate streamed notification counts, chunk sizing, last chunk sizing after GPT backup exclusion, invalid non-512-aligned chunks, and too-many-chunk errors. The test then recreates a small NVMe-oF-shared replica, writes random data, performs no-op and write-zero wipes, and compares the connected block device against `/dev/zero`.

State/persistence: transient pool/replica state and host NVMe device contents. The test mutates `replica.size` locally to account for reserved GPT backup bytes before expected-progress calculations.

Dependencies/integration: covers v1 test gRPC streaming, replica builder helpers, NVMe-oF connect/list utilities, host block-device comparison, and wipe implementation chunk accounting.

Risks: depends on host NVMe discovery returning exactly one Mayastor device and on `/tmp` bind mount/container privileges. Progress formulas are sensitive to GPT backup size and 512-byte alignment rules.

Test signals: passing test confirms streamed wipe responses are internally consistent and `WriteZeroes` actually clears device data while `None` does not.
