# subset-b-000467 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/topic/kafka/kafka.go -->
# sources/control-plane/rook/tests/integration/object/topic/kafka/kafka.go

Purpose: integration coverage for `CephBucketTopic` Kafka endpoint reconciliation in Rook's object-store tests. It builds a namespace, four Kubernetes Secrets, a bucket StorageClass, an OBC, a `CephBucketTopic`, and a `CephBucketNotification`, then drives updates through the Rook Ceph client and verifies RGW SNS state through an AWS SNS-compatible client.

Important APIs and control flow: helper `checkStatusSecrets` compares `CephBucketTopic.status.secrets` with live Secret name, namespace, UID, and ResourceVersion. `checkRgwTopicEndpoint` polls SNS `GetTopicAttributes`, parses the RGW endpoint JSON, and checks basic-auth user/password embedded in a `kafka://` endpoint. `cephBucketTopicReady` polls the CR until `ConditionReady` and a non-nil ARN. `TestBucketTopicKafka` skips TLS clusters, creates resources, waits for readiness, updates secret refs, removes refs, re-adds refs, mutates Secret data, deletes a referenced Secret to force `ReconcileFailed`, and finally deletes the notification, topic, OBC, StorageClass, Secrets, and namespace.

State, persistence, and integration: persistent state is Kubernetes CRs/Secrets/OBCs and RGW topic configuration. Dependencies include Rook clientsets, Kubernetes core/storage APIs, lib-bucket-provisioner OBC types, AWS SDK v2 SNS, and Rook object SNS utilities. Risks include long eventual-consistency windows, hard-coded Kafka endpoint assertions, and a suspicious cleanup/read typo where one Secret operation uses `secret3.Namespace` while addressing `secret4` or `secret2`; current namespace equality hides it. Test signals are strong because the test checks Kubernetes status references, RGW admin-visible endpoint attributes, failure state, and non-deletion of referenced Secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/topic/kafka/kafka.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/caps/caps.go -->
# sources/control-plane/rook/tests/integration/object/user/caps/caps.go

Purpose: integration test for `CephObjectStoreUser.spec.capabilities` reconciliation into RGW user caps. It creates a test namespace and one `CephObjectStoreUser` against a shared object store, then verifies default, configured, and removed capability states.

Important APIs and control flow: `TestObjectStoreUserCaps` uses Rook and Kubernetes clients, creates the namespace and user, polls until `ConditionReady`, builds a go-ceph RGW admin client via `util/admin.NewAdminClient`, reads the RGW user with `adminClient.GetUser`, updates `Spec.Capabilities` to buckets `*` and usage `read`, then sets capabilities back to nil. The comparison uses `go-cmp` against `[]admin.UserCapSpec`.

State, persistence, and integration: persistent state lives in the `CephObjectStoreUser` CR and RGW user record. The test depends on a non-TLS object store, the shared RGW admin credentials, and Rook reconciliation of caps. Risks are order-sensitive cap comparison and polling timeouts against slow RGW/operator startup. Test signals include empty default caps, exact configured caps, return-to-empty behavior, successful CR deletion, empty user list, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/caps/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/keys/keys.go -->
# sources/control-plane/rook/tests/integration/object/user/keys/keys.go

Purpose: integration test for explicit and generated key handling on `CephObjectStoreUser`. It validates that Secret-referenced S3 keys are reconciled into RGW user keys and exposed in CR status, and that transitions between explicit keys and operator-generated keys behave correctly.

Important APIs and control flow: `generateObjectStoreUserSecretName` mirrors the operator-generated Secret naming convention. `findUserKeySpec` searches RGW key specs by access key. `checkStatusKeys` compares `status.keys` with live Secret references including UID and ResourceVersion. `checkRgwUserKeys` polls RGW admin `GetUser` until each expected key is present and asserts no extra keys. `TestObjectStoreUserKeys` creates five Secrets, creates a user with three explicit key refs, updates to two refs, removes all refs to trigger one generated key, re-adds five explicit refs, mutates a referenced Secret, deletes a referenced Secret to force `ReconcileFailed`, and verifies deletion still succeeds.

State, persistence, and integration: state spans Kubernetes Secrets, `CephObjectStoreUser.status.keys`, the generated operator Secret, and RGW user key material. Dependencies include go-ceph RGW admin APIs, Rook clientsets, and shared object-store setup. Risks include hard-coded key material in test fixtures, reliance on exact generated Secret key names (`AccessKey`/`SecretKey` versus AWS-style keys), and eventual reconciliation latency. Test signals are broad: status reference fidelity, RGW key equality, generated-secret transition, missing-secret failure, final RGW user absence, and Secret retention after CR deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/keys/keys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go -->
# sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go

Purpose: integration coverage for `CephObjectStoreUser.spec.opMask` reconciliation. It verifies the default RGW operation mask, an explicit read-only mask, nil reset to default, and an explicitly empty mask.

Important APIs and control flow: `TestObjectStoreUserOpMask` creates a namespace and user, waits for `ConditionReady`, initializes a go-ceph admin client, verifies initial `OpMask` is `read, write, delete`, updates `Spec.OpMask` to a one-element slice containing `read`, removes it by setting nil, and then sets an empty slice to remove all operations. Each state is checked by polling `adminClient.GetUser`.

State, persistence, and integration: state lives in the user CR spec and RGW user metadata. It depends on Rook reconciliation and go-ceph admin access. Risks include string-format sensitivity in RGW's `OpMask` display (`<none>` versus empty) and the skipped TLS path. Test signals include exact admin API values for default, restricted, restored, and empty masks plus deletion and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/admin/admin.go -->
# sources/control-plane/rook/tests/integration/object/util/admin/admin.go

Purpose: shared helper for constructing a Ceph RGW admin API client during object integration tests. It abstracts credential lookup, endpoint discovery, TLS transport setup, and a basic admin API sanity check.

Important APIs and control flow: `NewAdminClient` calls `util/s3.GetS3Credentials` to read dashboard-admin RGW keys, `util/s3.GetS3Endpoint` to derive the object-store service endpoint, optionally installs an `http.Transport` with `InsecureSkipVerify` for test TLS clusters, then calls `admin.New` and verifies the client with `GetInfo`.

State, persistence, and integration: no durable state is created; it reads RGW credentials from `radosgw-admin` and Kubernetes service state. Dependencies include go-ceph RGW admin, Rook installer command execution, K8s helper, and S3 utility functions. Risks include intentionally disabled TLS verification, hard dependency on the dashboard-admin user and realm name, and endpoint port assumptions inherited from the S3 helper. Test signal is the immediate `GetInfo` call, which catches bad credentials or endpoints before callers run deeper assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/admin/admin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/s3/s3.go -->
# sources/control-plane/rook/tests/integration/object/util/s3/s3.go

Purpose: shared object integration helper for obtaining S3/RGW credentials and endpoint URLs. It feeds both RGW admin and SNS-compatible clients.

Important APIs and control flow: `GetS3Credentials` runs `radosgw-admin user info --uid=dashboard-admin --rgw-realm=<store>` through the installer, unmarshals JSON, and extracts the first `keys[0].access_key` and `secret_key`. `GetS3Endpoint` reads the Kubernetes Service named after the object store and returns `http://<ClusterIP>:80` or `https://<ClusterIP>:80` based on the TLS flag.

State, persistence, and integration: it reads RGW and Kubernetes service state but writes nothing. Dependencies include installer command execution, Kubernetes CoreV1 Services, JSON parsing, and Rook CephObjectStore metadata. Risks include unchecked JSON shape before type assertions on `keys[0]`, single-key assumptions, use of ClusterIP only, and port 80 even for HTTPS-enabled tests. Test signals come from downstream clients that immediately call admin `GetInfo` or SNS `ListTopics`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go -->
# sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go

Purpose: shared fixture for object integration tests that creates one reusable `CephObjectStore` and matching Service, reducing per-package setup cost. It explicitly allows object-store users from the test namespaces used by bucket-owner, Kafka topic, caps, keys, and opmask tests.

Important APIs and control flow: `Setup` constructs a single-replica object store named `test-shared` in `object-ns`, with metadata/data pools size 1 and gateway port 80. It creates the CR, polls until `Status.Phase == ConditionReady`, then creates a NodePort Service whose selector matches RGW labels and whose name matches the object store for `util/s3.GetS3Endpoint`. It returns the object store and a teardown closure.

State, persistence, and integration: creates durable Kubernetes CR and Service state, then deletes both during teardown. Dependencies include Rook Ceph APIs, Kubernetes Services, `intstr`, and `utils.Retry`. Risks include namespace preconditions, fixed names, single replica/no safe replica sizing, service target port 8080 assumption, and teardown that logs but does not fail if deletion fails. Test signals are readiness polling and immediate Service create success; downstream object tests validate RGW behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sns/sns.go -->
# sources/control-plane/rook/tests/integration/object/util/sns/sns.go

Purpose: shared helper for creating an AWS SDK v2 SNS client pointed at Ceph RGW's SNS-compatible endpoint. It is used by bucket-topic integration tests.

Important APIs and control flow: `snsResolverV2.ResolveEndpoint` converts a stored endpoint string into a Smithy endpoint. `NewClient` retrieves RGW credentials, loads AWS default config with static credentials and region `us-east-1`, gets the object-store endpoint, installs the custom endpoint resolver in `sns.NewFromConfig`, and sanity checks with `ListTopics`.

State, persistence, and integration: no state is written; it reads credentials and Kubernetes service data through S3 utilities and sends SNS API requests to RGW. Dependencies include AWS SDK v2 config/credentials/SNS, Smithy endpoints, Rook installer/K8s helpers, and CephObjectStore metadata. Risks include no TLS insecure transport override here despite endpoint scheme support, reliance on static dashboard-admin credentials, and region hard-coding. Test signal is the `ListTopics` sanity check before returning the client.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sns/sns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml -->
# sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml

Purpose: test `CephCluster` manifest for a PVC-backed encrypted OSD deployment. It is a compact cluster spec used by storage/encryption integration paths.

Important structure and control flow: the manifest defines `CephCluster/rook-ceph` in namespace `rook-ceph`, one monitor with a `manual` StorageClass PVC template, Ceph image `quay.io/ceph/ceph:v20.2.1` with unsupported versions allowed, dashboard disabled, host networking off, crash collector disabled, and one non-portable `storageClassDeviceSet` named `set1` with `encrypted: true` and a 10Gi block-mode data PVC.

State, persistence, and integration: creates Ceph cluster control-plane and OSD data state backed by Kubernetes PVCs and `/var/lib/rook`. Dependencies include Rook CRDs, a `manual` StorageClass, block PVs, and the specified Ceph image. Risks include single-replica/single-mon test topology, fixed image version, and destructive encrypted OSD state if reused outside disposable tests. Test signals are cluster readiness, encrypted PVC key Secret creation, and key rotation checks from related scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml -->
# sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml

Purpose: YAML fragment for enabling Ceph filesystem mirroring in a test manifest. It is not a full resource and is intended for composition or patching.

Important structure: under `spec.mirroring`, it sets `enabled: true`, adds a snapshot schedule for `/` every `24h`, and a snapshot retention entry for `/` with duration string `"h 24"`.

State, persistence, and integration: when merged into a `CephFilesystem`, it causes Rook/Ceph to manage mirroring and snapshot scheduling metadata. Dependencies include a consumer that inserts the fragment into a valid filesystem CR. Risks include fragment-only validity and the unusual retention duration format, which may intentionally exercise validation behavior. Test signals are accepted CR reconciliation and fs-mirror daemon/status checks in cluster validation scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-fs-mirror-spec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in -->
# sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in

Purpose: env-substituted Secret template for IBM Key Protect KMS tests. It supplies the API key used by Rook encryption configuration.

Important structure: defines `v1/Secret` named `rook-ibm-kp-token` in namespace `rook-ceph`, with `stringData.IBM_KP_SERVICE_API_KEY` populated from `$IBM_KP_SERVICE_API_KEY`.

State, persistence, and integration: creates a Kubernetes Secret consumed by `tokenSecretName: rook-ibm-kp-token` in the companion IBM Key Protect KMS spec fragment. Dependencies include environment substitution and Rook KMS integration. Risks include accidental plaintext key exposure in generated manifests/logs and missing environment variables producing unusable secrets. Test signals come from cluster encryption startup and key retrieval against IBM Key Protect.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in -->
# sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in

Purpose: env-substituted KMS configuration fragment for IBM Key Protect tests. It configures Rook's `spec.security.kms` section.

Important structure: sets `KMS_PROVIDER: ibmkeyprotect`, injects `$IBM_KP_SERVICE_INSTANCE_ID`, and points `tokenSecretName` to `rook-ibm-kp-token`.

State, persistence, and integration: when merged into a cluster spec, Rook uses IBM Key Protect for encryption key management. Dependencies include the companion Secret template, IBM service instance credentials, and a consuming manifest-generation path. Risks include fragment-only validity, unset substitutions, and external service availability. Test signals are encrypted OSD provisioning and key lifecycle operations succeeding through the KMS provider.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml

Purpose: Vault KMS cluster spec fragment using Kubernetes authentication. It is used with the Vault deployment/validation script to test Rook-managed encryption and key rotation.

Important structure: under `spec.security.kms.connectionDetails`, it sets Vault provider, in-cluster HTTPS address, backend path `rook/ver1`, `kv` engine, TLS file Secret names, `VAULT_SKIP_VERIFY`, auth method `kubernetes`, and role `rook-ceph`. `keyRotation` is enabled on a one-minute cron schedule.

State, persistence, and integration: when merged into a `CephCluster`, Rook OSDs authenticate to Vault with Kubernetes service accounts and store encryption keys under the configured backend. Dependencies include Vault TLS/client Secrets, the role set up by `deploy-validate-vault.sh`, and Rook service accounts. Risks include skip-verify in tests, frequent key rotation, and role/SA name coupling. Test signals are Vault secret count matching OSD PVC count and key material changing during rotation validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-k8s-auth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml

Purpose: Vault KMS cluster spec fragment using token authentication. It drives tests where Rook reads a Vault token from a Kubernetes Secret.

Important structure: configures Vault provider, HTTPS address, backend path `rook/ver1`, `kv` engine, TLS client/cert Secret names, `VAULT_AUTH_METHOD: token`, `tokenSecretName: rook-vault-token`, and one-minute key rotation.

State, persistence, and integration: cluster reconciliation mounts/reads the Vault token Secret and uses the configured backend for encryption keys. Dependencies include the generated `rook-vault-token` Secret and Vault TLS Secrets from the deployment script. Risks include token leakage, skip-verify test setting, and fragment-only validity. Test signals are successful OSD key creation and rotation through Vault token auth.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault-spec-token-auth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault.yaml -->
# sources/control-plane/rook/tests/manifests/test-kms-vault.yaml

Purpose: Secret manifest template for Vault token authentication tests. The deployment script replaces the placeholder with a base64-encoded Vault token.

Important structure: defines `v1/Secret` named `rook-vault-token` in namespace `rook-ceph` with `data.token: ROOK_TOKEN`.

State, persistence, and integration: creates a Kubernetes Secret consumed by `tokenSecretName: rook-vault-token` in token-auth KMS fragments. Dependencies include `deploy-validate-vault.sh` performing placeholder substitution after creating a Vault policy token. Risks include placeholder misuse, token exposure, and stale file mutation in the working tree. Test signals are Rook successfully authenticating to Vault and creating/rotating encryption keys.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-vault.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-object.yaml -->
# sources/control-plane/rook/tests/manifests/test-object.yaml

Purpose: small test `CephObjectStore` manifest for a single-OSD environment. It provides a minimal RGW object store named `my-store`.

Important structure: defines metadata and data pools with replicated size 1, `preservePoolsOnDelete: false`, gateway port 80, and one gateway instance. The comment indicates it is applied as an object test manifest.

State, persistence, and integration: creates RGW pools, deployment, and service state in the `rook-ceph` namespace. Dependencies include Rook object store CRDs and a functioning Ceph cluster. Risks include single-replica data loss assumptions, non-preserved pools on delete, and no secure port by default. Test signals are RGW pod readiness, service availability, and successful object API operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-object.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml -->
# sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml

Purpose: YAML fragment adding a BlueStore metadata device PVC template to a PVC-backed OSD device set. It is intended for composition into a larger cluster manifest.

Important structure: declares a volume claim template named `metadata` requesting 2Gi, `manual` StorageClass, block volume mode, and `ReadWriteOnce` access.

State, persistence, and integration: when inserted under `volumeClaimTemplates`, it provisions a separate block PVC used as BlueStore DB/metadata storage. Dependencies include a manual StorageClass and matching local PVs. Risks include fragment-only indentation sensitivity and insufficient 2Gi capacity if reused outside tests. Test signals are OSD prepare success and PVC binding for the metadata device.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-db.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml -->
# sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml

Purpose: YAML fragment adding a BlueStore WAL PVC template to a PVC-backed OSD device set. It complements the metadata/DB fragment for WAL-specific tests.

Important structure: declares a `wal` volume claim template requesting 2Gi, using `manual` StorageClass, block volume mode, and `ReadWriteOnce`.

State, persistence, and integration: when merged into a cluster storage device set, it provisions a separate WAL block PVC. Dependencies include local manual PV preparation and Rook OSD PVC orchestration. Risks include fragment-only YAML context and small fixed size. Test signals are bound WAL PVCs and successful OSD provisioning with WAL device assignment.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-on-pvc-wal.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/auto-grow-storage.sh -->
# sources/control-plane/rook/tests/scripts/auto-grow-storage.sh

Purpose: experimental automation for responding to Ceph OSD near-full/critical-full alerts by either resizing PVCs vertically or increasing OSD counts horizontally. It also bootstraps Prometheus prerequisites used to observe Rook alerts.

Important APIs and control flow: `calculateSize` normalizes Mi/Gi/Ti values into a global numeric unit, `compareSizes` compares desired and maximum sizes, `growVertically` patches a PVC storage request, `growHorizontally` locates the owning `storageClassDeviceSet` from PVC labels and patches its count, `growOSD` loops over Alertmanager alerts and invokes the chosen growth mode, `creatingPrerequisites` applies Prometheus operator and Rook monitoring manifests, and the command dispatcher accepts `count` or `size`.

State, persistence, and integration: it creates monitoring resources, reads Alertmanager through a toolbox pod, and patches PVCs or `CephCluster` specs. Dependencies include `kubectl`, `jq`, `bc`, Prometheus, Alertmanager service on node port 30900, Rook toolbox, and PVC-based OSDs. Risks include global variables, decimal unit approximations using 1000 not 1024, unquoted JSON patches, infinite loop behavior, hard-coded namespace/service assumptions, and live capacity-changing side effects. Test signals are printed patch results and subsequent Ceph/PVC state changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/auto-grow-storage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/build-release.sh -->
# sources/control-plane/rook/tests/scripts/build-release.sh

Purpose: release CI helper for building Rook, publishing images/docs, and promoting Helm charts for tagged releases.

Important APIs and control flow: it loads `.env`, rewrites `DOCS_GIT_REPO` to token-auth HTTPS when `GIT_API_TOKEN` exists, determines whether the run is master, release branch, or tag, resolves tag branch provenance with `git branch -r --contain`, runs `make build.all` and `make mod.check`, then invokes `make -C build/release build` and `publish`. `publish_charts` runs only for tagged releases.

State, persistence, and integration: writes build artifacts, pushes images/docs/charts, and may expose git status/diff in background. Dependencies include GNU make, git, AWS credentials, GitHub token, and Rook release make targets. Risks include exporting `.env` through `xargs`, backgrounded git diagnostics racing with output, and destructive publish side effects if environment variables are wrong. Test signals are make target success and optional chart promotion completion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/build-release.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/collect-logs.sh -->
# sources/control-plane/rook/tests/scripts/collect-logs.sh

Purpose: diagnostic log collector for Rook/Ceph test clusters. It captures Ceph status, Kubernetes resources, pod logs, CR descriptions, secrets, block device state, and host journals.

Important APIs and control flow: environment variables select cluster namespace, operator namespace, additional namespace, and output directory. The script runs Ceph commands through `rook-ceph-tools`, builds a namespace list, then for each namespace captures lists/descriptions/logs for pods, deployments, jobs, daemonsets, ConfigMaps, PVCs, and StorageClasses. It dumps Secrets as YAML, iterates all CRDs to describe namespace-scoped custom resources, and collects `kubectl get all`, `lsblk`, `dmesg`, and `journalctl`.

State, persistence, and integration: creates a filesystem log tree under `LOG_DIR` and reads sensitive cluster state. Dependencies include `kubectl`, toolbox deployment, `sudo`, and systemd journal access. Risks include collecting secret contents in plaintext, failures when resource kinds are absent, and large unbounded logs. Test signals are the presence of populated diagnostics for post-failure triage rather than pass/fail assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/collect-logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh -->
# sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh

Purpose: host-side test helper for wiping a block device and creating BlueStore-related partitions for Rook OSD tests.

Important APIs and control flow: parses `--disk`, optional `--bluestore-type block.db|block.wal`, `--osd-count`, and `--wipe-only`. `wipe_disk` zaps GPT/metadata and optionally exits after printing. `create_partition` creates fixed 2048M partitions named for DB/WAL. `create_block_partition` creates either one largest `block` partition or multiple 6144M OSD partitions and writes udev rules assigning Ceph UID/GID ownership. It finishes with `partprobe`, `udevadm settle`, `lsblk`, and `parted print`.

State, persistence, and integration: destructively modifies the selected disk and host udev rules. Dependencies include `sudo`, `sgdisk`, `dd`, `parted`, `partprobe`, and `udevadm`. Risks are severe if `DISK` is wrong, `OSD_COUNT` is unset, partition naming assumes simple `${DISK}${n}` device names, and udev size matching is hard-coded. Test signals are successful partition table output and later local PV/OSD provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-dev-cluster.sh -->
# sources/control-plane/rook/tests/scripts/create-dev-cluster.sh

Purpose: local developer helper for creating a Rook Ceph cluster on minikube. It supports custom namespaces, cluster spec selection, optional Rook orchestrator enablement, and monitoring setup.

Important APIs and control flow: environment variables configure minikube profile, disk size, node count, extra disks, examples dir, and namespaces. Functions initialize command aliases, rewrite namespace markers in example manifests, choose minikube driver by OS/architecture, create the cluster with CRDs/common/operator/cluster/toolbox/dashboard manifests, wait for operator and Ceph health, optionally enable the Ceph rook orchestrator and monitoring, and print dashboard/prometheus access details. Command options are `-f`, `-r`, `-m`, and `-h`.

State, persistence, and integration: creates/deletes a minikube profile, mutates files in the examples directory with `.bak` backups, applies Kubernetes resources, and changes the user's shell guidance. Dependencies include minikube, kubectl, envsubst, sed, base64, and Rook deploy examples. Risks include in-place manifest mutation, assumptions about minikube drivers, unquoted extra args, and infinite waits if health never reaches `HEALTH_OK`. Test signals are rollout status, cluster health, optional module status, and printed endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-dev-cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/csiaddons.sh -->
# sources/control-plane/rook/tests/scripts/csiaddons.sh

Purpose: CI helper for installing and verifying Kubernetes CSI-Addons integration with Rook CSI controller pods.

Important APIs and control flow: `setup_csiaddons` applies release CRDs/RBAC/controller manifests for version `v0.14.0` and patches `rook-ceph-operator-config` to set `CSI_ENABLE_CSIADDONS=true`. `verify_crd_created` checks the CSIAddonsNode CRD. `verify_container_in_pod_by_label` locates a Rook CSI controller pod by label and checks that the `csi-addons` container is ready. `verify_container_is_running` checks both RBD and CephFS controller plugins. The final dispatcher executes the named function.

State, persistence, and integration: creates cluster-level CRDs/RBAC/controller resources and patches a Rook ConfigMap. Dependencies include `kubectl`, internet access to GitHub release manifests, and Rook CSI controller labels. Risks include floating behavior if remote manifests change or disappear, no readiness wait after setup, and pod selection issues when multiple pods match. Test signals are CRD existence and ready sidecar container status.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/csiaddons.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh -->
# sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh

Purpose: integration helper for deploying a TLS-enabled Vault instance and validating Rook KMS behavior for OSD and RGW encryption, including key rotation.

Important APIs and control flow: startup installs `jq` and Helm on Linux. `deploy_vault` generates TLS files, creates Kubernetes TLS/client/CA Secrets, writes Helm values, installs Vault, initializes/unseals it, enables kv v1, kv v2, and transit engines, writes a Rook policy, and either configures Kubernetes auth or creates a token and patches `tests/manifests/test-kms-vault.yaml`. Validation paths inspect RGW pod Vault env/config, use curl with mounted TLS credentials to fetch KV or transit data keys, compare OSD PVC count to Vault secret count, and poll for rotated OSD key changes. The main case dispatches `deploy`, `validate_osd`, `validate_rgw`, or `validate_key_rotation`.

State, persistence, and integration: creates Vault Helm resources, multiple Kubernetes Secrets, Vault auth/policy/secret-engine state, and mutates a manifest token placeholder. Dependencies include Helm, kubectl, jq, OpenSSL/TLS generation script, Vault CLI in pod, Rook service accounts, and test manifests. Risks include plaintext token handling, in-place manifest mutation, broad Vault policy privileges, shell parsing of pod descriptions, and frequent key rotation timing. Test signals are Vault pod readiness, successful key fetch through RGW pod credentials, OSD secret count equality, and observed key rotation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/deploy-validate-vault.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/gen_release_notes.sh -->
# sources/control-plane/rook/tests/scripts/gen_release_notes.sh

Purpose: release utility for generating notes from GitHub pull requests using the `github-release-notes` (`gren`) container.

Important APIs and control flow: it validates that `GITHUB_USER` and `GITHUB_TOKEN` are set, defines `help`, and `release_notes` which runs `docker run --rm -e GREN_GITHUB_TOKEN=... githubchangeloggenerator/github-release-notes` with owner `rook`, repo `rook`, and the provided branch/tag argument. It dispatches directly to `release_notes "$1"`.

State, persistence, and integration: writes generated output to stdout and reads GitHub API state through the container. Dependencies include Docker, network access, GitHub token, and the external image. Risks include token exposure in process/container environment, external image drift, and no argument validation beyond credentials. Test signals are successful container completion and generated release-note content.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/gen_release_notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/generate-tls-config.sh -->
# sources/control-plane/rook/tests/scripts/generate-tls-config.sh

Purpose: helper for generating a simple CA, server certificate, and key for Vault or other in-cluster TLS test services.

Important APIs and control flow: it accepts output directory, service, namespace, and optional IP. If IP is omitted, it uses `127.0.0.1`. It writes OpenSSL config files, generates a CA key/cert, generates a service key/CSR with DNS SANs for service and namespace forms plus IP SAN, signs the CSR, and exports `CSR_NAME`.

State, persistence, and integration: writes certificate/key artifacts into the requested directory for later Secret creation. Dependencies include `openssl`, shell, and consumers such as `deploy-validate-vault.sh`. Risks include short-lived local private keys, minimal CA handling, and fixed SAN assumptions. Test signals are successful OpenSSL commands and downstream TLS clients connecting to the generated certs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/generate-tls-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/github-action-helper.sh -->
# sources/control-plane/rook/tests/scripts/github-action-helper.sh

Purpose: large GitHub Actions utility library and dispatcher for Rook CI workflows. It covers disk preparation, local builds, manifest deployment, cluster validation helpers, KMS/key checks, multisite object replication, Multus verification, CSI workloads, NVMe-oF workloads, and cleanup.

Important APIs and control flow: block-device helpers discover or create extra iSCSI disks, wipe runner devices, prepare loop devices, and create partitions/PVs. Build helpers retry network-like failures, validate modified files, and tag local images. Deployment helpers mutate example manifests for local images/log levels/loop devices, create prerequisites, deploy clusters/toolbox/additional resources, wait for prepare/cleanup pods, restart operator, and validate logs. Test helpers exercise Vault key rotation, owner references, multisite S3 replication with `s3cmd`, Multus connection addresses, CSI RBD/CephFS/NFS/NVMe-oF workloads, object separate pools, and Ceph auth key presence. The script ends by executing the function named by the first argument.

State, persistence, and integration: it mutates host disks, udev rules, example YAML files, Docker images, Kubernetes clusters, Ceph state, and local test files. Dependencies include Docker, make, Go, kubectl, yq v3, s3cmd, sudo disk tools, Helm-adjacent manifests, and many Rook deploy examples. Risks are high because functions are intentionally side-effectful: destructive disk wipes, in-place `sed`, broad cluster deletion, remote manifest pulls, time-sensitive waits, and function-name dispatch without allowlisting. Test signals are mostly command success, grep assertions, Ceph health output, workload writes/reads, and explicit diagnostic collection on failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/github-action-helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kube-api-lint.yaml -->
# sources/control-plane/rook/tests/scripts/kube-api-lint.yaml

Purpose: kube-api-linter configuration for validating Kubernetes API conventions in Rook code.

Important structure: the file configures linters and exceptions used by CI. It is a policy artifact rather than executable code, shaping which Kubernetes API patterns are accepted or ignored during lint runs.

State, persistence, and integration: no runtime state is created; CI tools read it when linting API types. Dependencies include kube-api-linter and its expected YAML schema. Risks include stale exceptions masking real API quality issues or config schema drift across linter versions. Test signals are kube-api-linter pass/fail results in CI.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kube-api-lint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kubeadm-install.sh -->
# sources/control-plane/rook/tests/scripts/kubeadm-install.sh

Purpose: host setup helper for installing a specified Kubernetes version via kubeadm packages on Debian/Ubuntu-like runners.

Important APIs and control flow: it defaults `KUBE_VERSION` to `v1.15.12`, converts it to Debian package suffix form, defines `wait_for_dpkg_unlock`, configures package repositories/keys, installs kubelet/kubeadm/kubectl, and marks packages held.

State, persistence, and integration: mutates apt sources, package state, and system Kubernetes binaries. Dependencies include apt, curl, root privileges, and package repository availability. Risks include old default Kubernetes version, package repository drift, and host-level side effects. Test signals are successful package install and later kubeadm cluster creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kubeadm-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/localPathPV.sh -->
# sources/control-plane/rook/tests/scripts/localPathPV.sh

Purpose: creates local PersistentVolumes and a manual StorageClass for Rook PVC-based integration tests, using host directories for monitors and block devices/partitions for OSDs, DB, and WAL.

Important APIs and control flow: it selects a scratch block device, validates it, labels the node, deletes previous `type=local` PVs, creates three filesystem monitor PVs under `/var/lib/rook/rook-integration-test`, optionally adds DB and WAL block PVs, chooses OSD count based on DB/WAL/LVM/test env, creates one or two OSD block PVs, then applies a `manual` no-provisioner StorageClass with `WaitForFirstConsumer`.

State, persistence, and integration: creates host directories, node labels, PVs, and a StorageClass. Dependencies include `kubectl`, `sudo`, `lsblk`, a valid block device, and local-path PV support. Risks include deleting all local-labeled PVs, fixed PV names, single-node assumption, and direct host path/block exposure. Test signals are `kubectl get pv -o wide` and subsequent PVC binding/OSD provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/localPathPV.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/loopDevicePV.sh -->
# sources/control-plane/rook/tests/scripts/loopDevicePV.sh

Purpose: creates block-mode local PVs pointing at `/dev/loopN` devices for loop-device OSD tests.

Important APIs and control flow: reads OSD count from the first argument, loops from 1 to that count, and applies a PV named `local-vol-loop-dev<N>` with `manual` StorageClass, 6Gi capacity, block volume mode, local path `/dev/loop<N>`, and node affinity for `rook.io/has-disk=true`.

State, persistence, and integration: creates PV resources that bind to later PVCs. Dependencies include pre-created loop devices, a labeled node, and `kubectl`. Risks include no argument validation, fixed PV names, and assumption that loop devices are safe and available. Test signals are PV listing and later PVC/OSD binding.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/loopDevicePV.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js -->
# sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js

Purpose: custom markdownlint rule enforcing MkDocs admonition formatting. It ensures admonition body text immediately follows the header and is indented four spaces beyond the header indent.

Important APIs and control flow: exports a markdownlint rule named `mkdocs-admonitions` with parser `none`. It iterates lines, detects headers starting with `!!!` after left trim, computes expected body indentation, reports an error and deletion fix for blank body lines, or a replacement indentation fix for incorrectly indented body lines.

State, persistence, and integration: no persistent state; markdownlint consumes it during docs checks. Dependencies include markdownlint's custom rule API. Risks include implicit global variables (`start_spaces`, `got_tab_spaces`), failure if the admonition header is the final line, and only checking the first body line. Test signals are markdownlint errors with autofix metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js -->
# sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js

Purpose: custom markdownlint rule enforcing indentation to exact four-space boundaries outside fenced code blocks.

Important APIs and control flow: exports rule `strict-tab-spacing`. It tracks fenced code block depth, counts leading spaces, and reports/fixes lines whose indentation is not divisible by four. It tries to infer whether to round down or up based on a two-space cutoff.

State, persistence, and integration: no persistent state; CI/docs lint tooling reads it. Dependencies include markdownlint custom rule contracts. Risks include implicit globals, simplistic code-fence tracking, and a likely fix calculation issue where `generateTabSpaces(floor)` treats the quotient as a raw space count instead of multiplying by four. Test signals are lint failures and generated fix information.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh -->
# sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh

Purpose: multi-node Vagrant helper that builds a local Rook image, pushes it to a local registry, rewrites deployment templates, and deploys Rook to a Vagrant Kubernetes cluster.

Important APIs and control flow: it verifies it is in a git repo, configures kubeconfig from the `k8s-01` VM, ensures the user can run Docker, starts a local registry, purges existing Rook/Ceph resources and VM Ceph disks, runs `make`, tags/pushes the build image to `172.17.8.1:5000/rook/ceph:latest`, rewrites `operator.yaml`, and creates operator/cluster manifests.

State, persistence, and integration: mutates kubeconfig, Docker registry/images, Kubernetes resources, Vagrant VM disks, and deploy examples. Dependencies include Vagrant, Docker, kubectl, make, and Rook example manifests. Risks include broad deletion of Rook resources and CRDs, destructive disk zeroing on VMs, image selection by regex, and older manifest names. Test signals are successful node listing, image push, CRD availability, and cluster creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/build-rook.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/config.rb -->
# sources/control-plane/rook/tests/scripts/multi-node/config.rb

Purpose: Vagrant/kubernetes multi-node test configuration values. It defines the base OS, box, node counts, and disk layout used by the multi-node scripts.

Important structure: uses CentOS 7, nine total instances, one etcd, one Kubernetes master, all instances as Kubernetes nodes, and two 20G disks for disk-enabled nodes.

State, persistence, and integration: consumed by the surrounding Vagrant environment to create VM topology and storage. Dependencies include Vagrant config conventions used by the Rook multi-node setup. Risks include old CentOS 7 base image, high local resource demand, and fixed disk sizing. Test signals are successful VM provisioning and availability of disks for Ceph OSD tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/config.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh -->
# sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh

Purpose: installs RPM-based host prerequisites for the multi-node Vagrant/libvirt Rook test environment.

Important APIs and control flow: `install_deps` scrapes the HashiCorp releases index for the latest Vagrant version, installs qemu/libvirt/Ruby/GCC/Docker/Kubernetes client/Go/git dependencies through yum, installs the Vagrant RPM, installs the `vagrant-libvirt` plugin, then starts Docker.

State, persistence, and integration: mutates system packages, Vagrant plugins, and Docker service state. Dependencies include yum, curl, internet access, HashiCorp release page structure, and systemd. Risks include latest-version scraping instability, lack of package pinning, and root-level host changes. Test signals are successful package/plugin install and Docker start.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml -->
# sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml

Purpose: NetworkAttachmentDefinition fixtures in the `default` namespace for Multus validation CLI tests.

Important structure: defines `public-net` as macvlan bridge on `eth0` with whereabouts IPv4 range `192.168.20.0/24` and route to `192.168.29.0/24`; defines `cluster-net` as macvlan bridge on `eth0` with whereabouts IPv6 range `fc00::/96`. The comment notes the mixed IPv4/IPv6 setup is unsuitable for CephCluster use but useful for validation tooling.

State, persistence, and integration: creates NAD CRs consumed by test pods launched by `rook multus validation`. Dependencies include Multus, whereabouts, and the `k8s.cni.cncf.io` API. Risks include hard-coded interface/ranges and intentionally invalid-for-Ceph cluster network. Test signals are validation CLI behavior against public/cluster network references.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml -->
# sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml

Purpose: test-only DaemonSet that configures each KinD/minikube node to route traffic to the Multus public network.

Important structure and control flow: runs privileged `jonlabelle/network-tools` pods on host networking, including control-plane toleration. The shell command derives the host `eth0` IP, creates a macvlan shim named `public-shim` using the last octet under `192.168.29.0/24`, and routes `192.168.20.0/24` through that shim before sleeping forever.

State, persistence, and integration: modifies host network interfaces/routes inside each node namespace while the DaemonSet is running. Dependencies include privileged pods, `NET_ADMIN`, macvlan support, and fixed network ranges matching NADs. Risks include non-production privileged networking, route conflicts, and hard-coded `eth0`. Test signals are pod readiness and successful connectivity from validation clients.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/kind-config.yaml -->
# sources/control-plane/rook/tests/scripts/multus/kind-config.yaml

Purpose: KinD cluster topology for Multus validation tests.

Important structure: defines one control-plane node and three worker nodes using `kind.x-k8s.io/v1alpha4`.

State, persistence, and integration: consumed by `kind create cluster` to provision a four-node test cluster. Dependencies include KinD and Docker. Risks include fixed node names assumed by label/taint scripts and local resource demand. Test signals are successful node creation and subsequent label/taint operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/kind-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml -->
# sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml

Purpose: NetworkAttachmentDefinition fixtures in the `rook-ceph` namespace for Rook Ceph Multus integration.

Important structure: defines `public-net` with whereabouts IPv4 range `192.168.20.0/24` and route to `192.168.29.0/24`; defines `cluster-net` with IPv4 range `192.168.21.0/24`. Both use macvlan bridge mode on `eth0`.

State, persistence, and integration: creates NADs referenced by Rook cluster network settings and connection tests. Dependencies include Multus, whereabouts, macvlan-capable nodes, and matching host route DaemonSet. Risks include hard-coded subnets/interface and namespace coupling. Test signals include Ceph daemon address checks showing OSDs on both public and cluster networks and MDS only on public.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/setup-multus.sh -->
# sources/control-plane/rook/tests/scripts/multus/setup-multus.sh

Purpose: installs Multus, CNI plugins, and whereabouts into a test Kubernetes cluster.

Important APIs and control flow: waits for CoreDNS, uses a retry wrapper around `kubectl create` for the Multus daemonset URL, waits for Multus pods, creates CNI install manifests, waits for CNI plugin pods, then applies whereabouts daemonset and CRDs and waits for whereabouts pods. Timeouts and retry counts are configurable through variables at the top.

State, persistence, and integration: creates cluster networking components under kube-system plus whereabouts CRDs. Dependencies include remote raw GitHub manifests, kubectl, CoreDNS availability, and `timeout`. Risks include using `master` branch remote manifests, command-string retry quoting, and create failures on re-runs due to existing resources. Test signals are ready pods for Multus, CNI plugins, and whereabouts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/setup-multus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/stretch.yaml -->
# sources/control-plane/rook/tests/scripts/multus/stretch.yaml

Purpose: configuration file for `rook multus validation run` stretch-cluster scenarios. It models arbiter, storage, and worker node types with different daemon counts and placements.

Important structure: sets namespace `stretch-test`, public/cluster network names, timeouts, nginx image, and three node types. Arbiter nodes have no OSDs and one other daemon on zone `arbiter` with control-plane toleration. Storage nodes have two OSD clients and three other clients on `storage-node=true` with matching toleration. Worker nodes default to zero OSDs and two other clients with no placement.

State, persistence, and integration: consumed by the Rook CLI validation tool to create test resources and clients. Dependencies include labeled/tainted KinD nodes and NADs. Risks include overlap unless nodes are tainted/labeled correctly, fixed image, and namespace mutation by test scripts. Test signals are expected client-count log lines and cleanup assertions in the Multus scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/stretch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh

Purpose: smoke test for direct `rook multus validation run` CLI arguments without a config file.

Important APIs and control flow: creates namespace `cli-test`, creates the expected `rook-ceph-system` service account, runs `./rook --log-level DEBUG multus validation run` with namespace, public and cluster networks in `default`, and two daemons per node, then greps output for expected client startup and readiness lines. It asserts no non-terminating pods remain.

State, persistence, and integration: creates namespace/serviceaccount and temporary validation resources that should be cleaned by the CLI. Dependencies include built `./rook`, default NADs, and Multus. Risks include fixed expected client count of six and log-string coupling. Test signals are grep matches and empty namespace pod list after success.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh

Purpose: prepares KinD nodes with topology and storage labels for Multus stretch validation tests.

Important APIs and control flow: labels `kind-control-plane` as zone `arbiter`, `kind-worker` as zone `dc1` and storage node, `kind-worker2` as zone `dc2` and storage node, and `kind-worker3` as zone `dc2`.

State, persistence, and integration: mutates Kubernetes Node labels consumed by `stretch.yaml` placement rules. Dependencies include exact KinD node names. Risks include failing on non-KinD clusters or reruns where labels need overwrite. Test signals are subsequent validation selecting correct node groups.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh

Purpose: adds NoSchedule taints to storage worker nodes so worker and storage node-type placements do not overlap in stretch validation tests.

Important APIs and control flow: taints `kind-worker` and `kind-worker2` with `storage-node=true:NoSchedule`.

State, persistence, and integration: mutates Kubernetes Node taints and relies on matching tolerations in `stretch.yaml` for storage-node clients. Dependencies include exact KinD node names. Risks include rerun/idempotency issues without `--overwrite` or taint removal handling. Test signals are the overlap test failing before this setup and success tests passing after it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh

Purpose: negative Multus validation test proving that overlapping node-type selections are detected.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` into `stretch-overlap.yaml` with default namespace NADs, runs the validation command expecting failure, greps for the exact overlap error between worker and storage node types, and asserts pods remain for debugging.

State, persistence, and integration: creates namespace, serviceaccount, generated config, output log, and validation pods left intentionally after failure. Dependencies include labels without storage taints, built `./rook`, Multus, and default NADs. Risks include exact error-message coupling and intentional leftover resources requiring cleanup. Test signals are command failure, grep match, and non-empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh

Purpose: cleanup test for resources left by the negative Multus overlap validation.

Important APIs and control flow: runs `./rook --log-level DEBUG multus validation cleanup --namespace stretch-overlap` and asserts no non-terminating pods remain in that namespace.

State, persistence, and integration: deletes validation resources in the overlap namespace. Dependencies include the built Rook CLI and resources from `test-210-stretch-overlap.sh`. Risks include namespace/resource leakage if cleanup misses kinds beyond pods. Test signals are an empty pod list after cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh

Purpose: positive stretch validation scenario with both public and cluster networks configured.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to use default NADs and the test namespace, runs the validation CLI, greps output for expected OSD and non-OSD client counts for arbiter, storage, and worker node types, checks total readiness of 13 clients, and asserts cleanup leaves no pods.

State, persistence, and integration: creates temporary namespace resources, generated config, and output log. Dependencies include labeled/tainted nodes, Multus/default NADs, and built `./rook`. Risks include expected-count and log-string coupling. Test signals are grep matches and empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh

Purpose: positive stretch validation scenario with only a public network configured.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to set public network and blank cluster network, runs the validation CLI, greps expected client counts for all node types, checks 13 ready clients, and verifies pod cleanup.

State, persistence, and integration: creates temporary validation resources and a generated config/log. Dependencies include public NAD, node labels/taints, Multus, and the Rook CLI. Risks include log-string coupling and fixed client counts. Test signals are expected grep lines and no remaining pods.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh

Purpose: positive stretch validation scenario with only a cluster network configured, where only OSD clients should run.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to blank public network and set cluster network, runs the validation CLI, greps OSD startup counts for each node type, checks that four clients become ready, and verifies cleanup.

State, persistence, and integration: creates temporary validation resources and generated config/log files. Dependencies include cluster NAD, node labels/taints, Multus, and built `./rook`. Risks include exact client count assumptions and not checking absence of non-OSD log lines. Test signals are grep matches for OSD counts, total ready clients, and empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile -->
# sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile

Purpose: minimal container image definition for the Python request-logging web server used in tests.

Important structure: uses `python:3`, adds `server.py` at image root, exposes port 8080, and runs `python ./server.py`.

State, persistence, and integration: creates an image layer containing the server script and exposes a simple HTTP endpoint at runtime. Dependencies include Docker build and the Python base image. Risks include unpinned base image drift, broad `ADD`, and no non-root user. Test signals are container startup and ability to accept/log POST requests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/server.py -->
# sources/control-plane/rook/tests/scripts/pythonwebserver/server.py

Purpose: tiny HTTP server for tests that need an endpoint receiving and logging POST bodies.

Important APIs and control flow: class `S` extends `BaseHTTPRequestHandler`; `_set_response` would send a 200 HTML response but is not called by `do_POST`. `do_POST` reads `Content-Length` bytes and logs the decoded body. `run` starts an `HTTPServer` on all interfaces and a requested or default port 8080, handling KeyboardInterrupt for shutdown.

State, persistence, and integration: it does not persist request bodies except to process logs. Dependencies are Python standard library HTTP server and logging modules. Risks include `do_POST` not sending a response, missing/invalid `Content-Length` handling, no GET handler, and single-threaded serving. Test signals are log lines showing received POST body and process availability.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/tmate-pod.yaml -->
# sources/control-plane/rook/tests/scripts/tmate-pod.yaml

Purpose: CI debugging manifest that deploys a tmate session into a cluster for interactive troubleshooting.

Important structure: creates namespace `tmate`, service account, all-powerful ClusterRole and binding, and a Deployment running Fedora 39. The container installs tmate, kubernetes-client, bash, and vim, then runs `tmate -F` with a socket readiness probe.

State, persistence, and integration: creates privileged-by-RBAC debugging access to the whole cluster and exposes tmate connection details in logs. Dependencies include package install from Fedora repos and cluster network egress. Risks are intentionally severe security exposure through cluster-admin-like RBAC and remote shell access; it should only be applied to disposable CI clusters. Test signals are pod readiness and tmate log output containing SSH/web links.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/tmate-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_cluster.sh -->
# sources/control-plane/rook/tests/scripts/validate_cluster.sh

Purpose: cluster readiness validator for Rook/Ceph demo and integration environments. It checks CSI pods and selected Ceph daemons through toolbox and Kubernetes status.

Important APIs and control flow: first argument chooses daemons or defaults to `all`; second is OSD count or object-store name for RGW. `wait_for_daemon` retries command predicates. Dedicated tests check mon quorum, mgr presence, OSD up/in count, RGW pod readiness, MDS pools/up status, rbd-mirror, fs-mirror, pool count, CSI pod minimum, and NFS pod count. Main always checks CSI, mon, and mgr, then expands daemon list and runs selected checks, finally printing Ceph status, pods, operator logs, and cluster YAML.

State, persistence, and integration: reads cluster state and logs but does not create resources. Dependencies include a `rook-ceph-tools` deployment, `kubectl`, Ceph CLI, and expected labels/resource names. Risks include grep-string fragility, `log` function references in the error path without definition, and assumptions about namespace `rook-ceph`. Test signals are successful predicates and diagnostic output on failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_modified_files.sh -->
# sources/control-plane/rook/tests/scripts/validate_modified_files.sh

Purpose: CI guard ensuring generated files or build steps did not leave uncommitted changes after running make targets.

Important APIs and control flow: defines error messages by validation category. `validate` captures `git status --porcelain`, iterates non-empty output tokens, prints the category-specific error, full status, and `git diff`, then exits 1. The main case maps arguments such as `docs`, `helm-docs`, `codegen`, `modcheck`, `crd`, `build`, and `gen-rbac` to messages.

State, persistence, and integration: reads git worktree state and emits diffs; it writes nothing. Dependencies include git and a clean expected worktree after generation. Risks include iterating whitespace-split status output, noisy diffs for unrelated changes, and a typo in the build error string. Test signals are zero `git status --porcelain` output after the relevant CI step.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_modified_files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java

Purpose: Alluxio UFS output stream that provides atomic file creation by writing to a temporary path and renaming to the permanent path on close. It also implements `ContentHashable` for post-write fingerprinting.

Important APIs and control flow: the constructor derives a random temporary file name near the target path and calls `AtomicFileOutputStreamCallback.createDirect`. `write` methods delegate to the temporary stream. `close` is idempotent, closes the temporary stream, renames temp to permanent, deletes temp and throws if rename fails, then optionally preserves owner/group from `CreateOptions`. `getContentHash` reads the permanent file status and returns its content hash.

State, persistence, and integration: persists bytes first at a temporary UFS path and then at the final path after rename. Dependencies include callback methods from the concrete UFS, `PathUtils.temporaryFileName`, `IdUtils`, `CreateOptions`, and UFS status metadata. Risks include temp-file leakage if close is never called, atomicity depending on UFS rename semantics, and content hash lookup only after close/permanent path availability. Test signals should cover rename failure cleanup, owner/group preservation, idempotent close, and content hash retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java

Purpose: callback interface for UFS implementations that support `AtomicFileOutputStream`. It extends `UnderFileSystem` with a direct-create operation used for temporary writes.

Important APIs and control flow: declares `createDirect(String path, CreateOptions options)` returning an `OutputStream` that writes directly to storage without atomicity guarantees. `AtomicFileOutputStream` uses normal UFS operations from the inherited interface for rename, delete, owner update, and status lookup.

State, persistence, and integration: no state itself; implementers decide how direct temporary writes are persisted. Dependencies include the broader `UnderFileSystem` contract and `CreateOptions`. Risks include implementers accidentally routing `createDirect` back through atomic creation and recursion, or not matching option semantics. Test signals are concrete UFS tests that atomic streams create temp files directly and publish only on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/BaseUnderFileSystem.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/BaseUnderFileSystem.java

Purpose: base abstract implementation of Alluxio `UnderFileSystem` and `UfsClient` with default behavior for common operations, fingerprinting, recursive listing, async listing, ACL no-ops, operation mode, active sync stubs, and URI resolution.

Important APIs and control flow: constructor stores URI/config, creates a cached async IO executor, and initializes a metadata sync rate limiter from configuration. Defaults include `create` with parent creation, `deleteDirectory` default options, `exists` via `isFile`/`isDirectory`, empty ACL pair, parsed and serialized fingerprints with optional ACL/content hash, object-storage and seekable false defaults, recursive `listStatus` breadth-first traversal, and `performListingAsync` that optionally checks base status, handles object-storage edge cases, lists recursively or directly, normalizes names to full paths, and calls completion/error callbacks.

State, persistence, and integration: owns an executor service and rate limiter; otherwise delegates persistence to concrete UFS implementations. Dependencies include Alluxio URI/config/options/status/fingerprint classes, Guava `Closer`/`Iterators`, Java streams, and `PathUtils`. Risks include OOM for non-object stores using batch iterable fallback, async listing callback streams that must be consumed correctly, object-store synthetic-directory special cases, and default no-op ACL/active-sync behavior masking unsupported features. Test signals should exercise recursive listing names, async listing for missing/file/directory/object-storage paths, fingerprint invalidation on exceptions, executor shutdown on close, and rate limiter config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/BaseUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java

Purpose: adapter base for UFS implementations that do not suffer eventual-consistency issues. It maps guarded "existing", "nonexisting", and "renamable" operations directly to normal UFS operations.

Important APIs and control flow: `createNonexistingFile` calls `create`, delete-existing calls `deleteDirectory`/`deleteFile`, get-existing status methods call their normal equivalents, `isExistingDirectory` calls `isDirectory`, open-existing calls `open`, and rename-renamable calls `renameDirectory`/`renameFile`.

State, persistence, and integration: no additional state beyond `BaseUnderFileSystem`. It changes behavioral assumptions for concrete subclasses by trusting immediate consistency. Dependencies include Alluxio URI/config and UFS options. Risks include misuse for eventually consistent object stores, which would bypass protective checks expected elsewhere. Test signals should verify subclasses inherit the direct mappings and that higher layers select this base only for truly consistent UFS backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java

Purpose: marker/extension interface for output streams that can return a content hash after writing to the UFS. Alluxio uses this hash in metadata fingerprints when completing files.

Important APIs and control flow: declares `Optional<String> getContentHash() throws IOException`. Implementations such as atomic or object output streams decide when the hash is available and whether it can be absent.

State, persistence, and integration: interface only; state lives in implementing streams and UFS metadata. Dependencies include `Optional` and the `UnderFileSystem#create` contract described in comments. Risks include callers asking before close, backend hashes that are not stable across multipart/single uploads, and `Optional.empty` handling. Test signals include file completion paths incorporating returned hashes into fingerprints when present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java

Purpose: serializable metadata/content fingerprint for UFS files and directories. It captures type, UFS type, owner, group, mode, optional content hash, and optional ACL for change detection.

Important APIs and control flow: `create` builds tag maps from `UfsStatus`, optional content hash, and optional ACL; files include `CONTENT_HASH`, directories do not. `parse` converts serialized `TAG|value` pairs back into a fingerprint and validates required tags. `serialize` emits required tags first then optional tags. `matchMetadata` compares owner/group/mode/ACL; `matchContent` compares type/UFS/content hash. `putTag` sanitizes values by replacing pipe and space with underscores, while missing tags read as `_`.

State, persistence, and integration: state is an internal mutable `Map<Tag,String>` despite final class and not-thread-safe annotation. Dependencies include Alluxio constants/status classes, ACL stringification, Guava `Splitter`, Apache `StringUtils`, and UFS type names. Risks include parse throwing on malformed enum names/key-value strings, lossy sanitization causing collisions, missing optional tags comparing as `_`, and mutable fingerprints after creation. Test signals should cover invalid fingerprints, serialization ordering, ACL inclusion, file versus directory content matching, and sanitization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java

Purpose: abstract input stream for object stores that reads data through bounded range requests instead of holding one long stream to object end. It is designed for chunked reads and efficient skips.

Important APIs and control flow: constructor stores range chunk size. `read()` and `read(byte[],off,len)` lazily `openStream`, delegate to the current range stream, advance `mPos`, and close the range stream once `mPos >= mEndPos`. `skip` closes any current stream, advances `mPos`, and opens a new range. `openStream` rejects closed streams and non-positive chunk sizes, computes the next range end aligned to the chunk boundary, and calls abstract `createStream(startPos,endPos)`.

State, persistence, and integration: maintains current logical position, current range end, and backing input stream. Dependencies are concrete object-store subclasses that implement byte-range `createStream`. Risks include `skip` returning `n` even if beyond content length, undefined behavior for invalid ranges delegated to subclasses, and not thread-safe state. Test signals should cover chunk-boundary reopening, close idempotency, invalid chunk size, skip behavior, and EOF across ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectLowLevelOutputStream.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectLowLevelOutputStream.java

Purpose: abstract experimental output stream for streaming writes to object storage using low-level multipart upload. It buffers writes to local temp files, uploads full partitions asynchronously, and completes or aborts multipart uploads through subclass hooks.

Important APIs and control flow: constructor validates bucket/tmp dirs, initializes MD5 hashing, partition size, part counter, executor, and optional per-part timeout. `write` initializes a temp file as needed, writes into it until partition size, then calls `uploadPart` and recursively writes the remainder. `flush` uploads the current file if multipart is initialized and it exceeds 5 MiB, then waits for outstanding futures. `close` is idempotent and not retried: if multipart never started, it either creates an empty object or single `putObject` with MD5; otherwise it uploads the last part, waits for futures, and completes the multipart upload. `uploadPart` initializes multipart on first part, closes the local file, submits retrying async upload, and deletes temp files in `finally`. `waitForAllPartsUpload` handles execution failure, interruption, and timeout by cancelling futures and aborting multipart.

State, persistence, and integration: persists temporary files under configured Alluxio temp dirs, tracks MD5 digest per local file, part numbers, future list, closed flag, and multipart initialized flag. Subclasses provide storage-specific `init`, `uploadPartInternal`, `complete`, `abort`, `createEmptyObject`, and `putObject`. Dependencies include Alluxio configuration keys, retry utilities, Guava listenable futures, Base64 MD5 encoding, and object-store semantics requiring >=5 MiB non-final parts. Risks include temp-file leakage on process death, incomplete multipart uploads requiring external cleanup, MD5 digest reset per temp file rather than whole object, close setting `mClosed` before all failures, and interruption path not throwing after abort. Test signals should cover single-put versus multipart paths, flush threshold, retry/abort on future failure/timeout, part-number sequence, temp deletion, empty object creation, and subclass hook invocation order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectLowLevelOutputStream.java -->
