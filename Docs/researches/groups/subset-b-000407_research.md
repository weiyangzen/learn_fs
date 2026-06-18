# Research: subset-b-000407

Grouped research for the Longhorn deployment manifest, prerequisite host-prep manifests, upgrade responder assets, development scripts, storage examples, network policies, snapshots, and Renovate configuration. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/longhorn.yaml -->
# sources/control-plane/longhorn/deploy/longhorn.yaml

Purpose: rendered install manifest for a development Longhorn control plane in `longhorn-system`. It creates the namespace, priority class, service accounts, default setting/resource/storage-class config maps, Longhorn CRDs, broad RBAC, backend/UI/webhook/recovery services, the manager DaemonSet, CSI driver deployer, and UI deployment.

Important APIs/types/functions: Kubernetes APIs include `Namespace`, `PriorityClass`, `ServiceAccount`, `ConfigMap`, `CustomResourceDefinition`, RBAC resources, `Service`, `DaemonSet`, and `Deployment`. Longhorn API types under `longhorn.io/v1beta2` include backing images/data sources/managers, backups, backup targets/volumes/backing images, engine frontends/images/engines, instance managers, nodes, orphans, recurring jobs, replicas, settings, share managers, snapshots, support bundles, system backups/restores, volume attachments, and volumes.

Control flow: installation registers CRDs before controllers, grants the manager cluster and namespace permissions, exposes manager ports 9500/9502/9503, runs `longhorn-manager -d daemon` on every node, waits for the backend before `longhorn-manager -d deploy-driver`, and runs two UI replicas pointed at `http://longhorn-backend:9500`. The manager then reconciles CRDs and deploys runtime CSI/engine/replica/share-manager components from the configured images.

State and persistence: Kubernetes stores desired and observed state in CRDs with `/status` subresources. Volume data persists on host path `/var/lib/longhorn/`; manager pods mount `/boot`, `/dev`, `/proc`, `/etc`, and optional `longhorn-grpc-tls`. ConfigMaps seed default settings and a default `driver.longhorn.io` StorageClass with replica, timeout, filesystem, data locality, unmap, data engine, and backup target parameters.

Dependencies/integration points: depends on Kubernetes CRD/status, RBAC, storage, snapshot, admission registration, metrics, discovery, CSI sidecars, host block devices, iSCSI/NFS support, and Longhorn container images. It integrates with webhook admission on 9502, recovery backend on 9503, CSI provisioning through the driver deployer, and support bundle collection with a separate cluster-admin binding.

Risks/test signals: the manager is privileged and host-mounted, RBAC includes `*` on CRDs/storage/snapshot/Longhorn resources, and support bundle service account binds `cluster-admin`. Image tags are `master-head`, making reproducibility weaker than pinned releases. Test signals are `kubectl apply --dry-run=server`, CRD schema validation, rollout/readiness of manager/driver/UI, default StorageClass creation, webhook health, PVC provisioning, volume attach/detach, snapshot/backup flows, and host-path mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/longhorn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml -->
# sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml

Purpose: legacy PodSecurityPolicy and namespace RBAC allowing Longhorn pods to run with the privileges required for host storage operations.

Important APIs/types/functions: defines `policy/v1beta1` `PodSecurityPolicy` named `longhorn-psp`, an RBAC `Role` granting `use` on that PSP, and a `RoleBinding` for `longhorn-service-account` and the namespace `default` service account.

Control flow: clusters that still support PSP admit Longhorn pods through this policy when the bound service accounts create pods. The policy allows privileged mode, privilege escalation, `SYS_ADMIN`, hostPath volumes, host PID, and broad user/group/SELinux strategies while dropping `NET_RAW`.

State and persistence: it stores only admission policy and RBAC objects. There is no application data persistence, but the policy permits hostPath mounts used by Longhorn runtime pods.

Dependencies/integration points: depends on the removed `policy/v1beta1` PodSecurityPolicy API, so it only applies to older Kubernetes versions or distributions that retain PSP. It integrates with Longhorn service accounts in `longhorn-system`.

Risks/test signals: PSP is obsolete on modern Kubernetes, and the granted privileges are intentionally broad. Test signals are server-side apply against target cluster versions, pod admission checks for manager/instance pods, and verification that replacement Pod Security Admission labels or distribution-specific policies cover equivalent privileges.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml

Purpose: node-wide helper DaemonSet for installing `cifs-utils`, enabling Longhorn backup targets or workflows that require CIFS support on every node.

Important APIs/types/functions: defines an `apps/v1` `DaemonSet` with a privileged init container running `nsenter --mount=/proc/1/ns/mnt -- bash -c <cmd>` and a pause container to keep the pod present.

Control flow: each node enters the host mount namespace, detects distro family from `/etc/os-release`, then runs `apt-get`, `zypper`, or `yum` commands to install `cifs-utils`. The init container prints success or failure, then the pause container holds the DaemonSet pod.

State and persistence: mutates host OS package state outside Kubernetes. Kubernetes only stores the DaemonSet/pod status; the installed package remains on the node image or filesystem until manually changed.

Dependencies/integration points: depends on host package managers, network access to package repositories, `sudo`, `bash`, `nsenter`, and privileged host namespace access. It integrates with Longhorn backupstore support that needs CIFS mounting.

Risks/test signals: running package managers from a pod is distro-sensitive, non-idempotent under partial failures, and can drift immutable nodes. Test signals are DaemonSet rollout, init container logs, `mount.cifs` availability on every node, and backup target mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml

Purpose: GKE COS node agent that prepares the containerized mounter rootfs for Longhorn data paths and keeps `iscsid` plus `iscsi_tcp` available.

Important APIs/types/functions: defines a ConfigMap containing `entrypoint.sh` and a privileged DaemonSet using `registry.suse.com/bci/bci-base:15.5`. Script functions include `mount_longhorn_data_dir_on_host`, `is_mounted_on_host`, `is_module_loaded_on_host`, `load_iscsi_tcp_module_on_host`, and `install_and_start_iscsid`.

Control flow: the DaemonSet mounts host `/` at `/host`, reads comma-separated `LONGHORN_DATA_PATHS`, creates paths in host and containerized mounter rootfs, bind-mounts and marks them shared, remounts the Longhorn path executable, installs open-iscsi with `zypper`, starts `/sbin/iscsid`, loads `iscsi_tcp`, then sleeps forever. Liveness and readiness probes verify `iscsid` and the kernel module through `nsenter`.

State and persistence: changes host mount namespace, host directories, package state inside the agent container/rootfs, running daemon state, and kernel module state. Kubernetes persists the ConfigMap and DaemonSet only.

Dependencies/integration points: depends on GKE COS layout `/home/kubernetes/containerized_mounter/rootfs`, privileged mount namespace access, `chroot`, `nsenter`, `findmnt`, `zypper`, `iscsid`, and `modprobe`. It integrates with Longhorn iSCSI attachment and data path access on COS nodes.

Risks/test signals: path assumptions are GKE/COS-specific; bad `LONGHORN_DATA_PATHS` or mount propagation can break data path visibility. Test signals are DaemonSet readiness, probe stability, `findmnt` output on host, loaded `iscsi_tcp`, running `iscsid`, and successful Longhorn volume attach on COS nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml

Purpose: Fedora/RHEL-style SELinux workaround that grants `iscsid_t` `dac_override` capability needed by Longhorn iSCSI flows on affected systems.

Important APIs/types/functions: defines a privileged DaemonSet whose init container uses `nsenter` into the host mount namespace and runs `rpm`, writes a temporary CIL module, applies it with `semodule -vi`, and deletes the temporary file.

Control flow: each node checks for `policycoreutils` via `rpm -q`; if available, it writes `(allow iscsid_t self (capability (dac_override)))` into `/tmp/local_longhorn.cil`, installs it, reports status, then leaves a pause container running.

State and persistence: mutates host SELinux policy module state. Kubernetes stores only DaemonSet and pod status; SELinux policy persists independently on the host.

Dependencies/integration points: depends on SELinux-enabled RPM distributions, `policycoreutils`, `semodule`, `bash`, and privileged host namespace access. It integrates with host `iscsid` access for Longhorn volumes.

Risks/test signals: applies a host security policy exception and is inapplicable outside Fedora-like systems. Test signals are init logs, `semodule -l` on hosts, absence of SELinux AVC denials for Longhorn iSCSI operations, and successful attach/mount under enforcing SELinux.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml -->
# sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml

Purpose: Helm values for deploying Longhorn's upgrade responder service with release metadata, telemetry schema, image settings, resources, and chart source metadata.

Important APIs/types/functions: top-level values include `applicationName`, `image`, `secret`, `resources`, `flags.scarfEndpoint`, `configMap.responseConfig`, `configMap.requestSchema`, `url`, `commit`, `releaseName`, and `namespace`. The embedded JSON defines stable/latest versions and request schemas for tags and numeric fields.

Control flow: the upgrade responder chart consumes these values to create application-specific database/configuration and answer version-check requests. `responseConfig` marks `v1.11.2` as latest/stable in this file, and `requestSchema` validates reported Longhorn environment, settings, counts, and resource metrics.

State and persistence: no runtime state in the file itself; deployed chart stores config in ConfigMaps/Secrets and writes collected check-in data to the configured InfluxDB database.

Dependencies/integration points: integrates with `longhornio/upgrade-responder:longhorn-head`, Scarf gateway endpoints, Helm, InfluxDB, and Longhorn manager's version-check payload shape.

Risks/test signals: schema drift can cause upgrade checks to reject new Longhorn fields or silently omit metrics. Version metadata can become stale. Test signals are Helm template validation, JSON parsing of embedded blocks, upgrade responder startup, `/v1/checkupgrade` responses, and ingest tests with representative Longhorn payloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml -->
# sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml

Purpose: minimal chart metadata pointer for the Longhorn upgrade responder deployment.

Important APIs/types/functions: declares chart `url` as the upgrade responder GitHub repository, a pinned `commit`, `releaseName: longhorn-upgrade-responder`, and `namespace: longhorn-upgrade-responder`.

Control flow: automation can use this file to locate the chart source and deploy a known revision under the specified release/namespace.

State and persistence: no runtime state; it is deployment metadata.

Dependencies/integration points: depends on the upgrade responder repository and the pinned commit being fetchable. It complements `chart-values.yaml`.

Risks/test signals: stale commits or moved repositories break reproducible deployment. Test signals are repository fetch, commit checkout, Helm chart discovery, and consistency with the values file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/sample.sh -->
# sources/control-plane/longhorn/dev/scale-test/sample.sh

Purpose: simple scale helper that scales all StatefulSets to a per-node replica count and waits until a requested number of pods report ready.

Important APIs/types/functions: shell variables `requested`, `node_count`, `required_scale`; `kubectl scale --replicas=<required_scale> statefulset --all`; readiness counting via `kubectl get pods ... containerStatuses[*].ready | grep -c true`.

Control flow: computes `requested / node_count`, logs initial ready count, scales all StatefulSets in the current namespace/context, then polls every 60 seconds until ready count equals the requested total.

State and persistence: mutates live Kubernetes StatefulSet replica counts. It persists no local state.

Dependencies/integration points: depends on `kubectl`, current kube context, shell arithmetic, and pod readiness fields. It is intended to pair with generated scale-test StatefulSets.

Risks/test signals: integer division can under-scale, `grep -c true` can miscount multi-container pods, and `statefulset --all` is broad. Test signals are dry-run/manual namespace scoping, observed replica counts, and readiness convergence for generated workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/sample.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/scale-test.py -->
# sources/control-plane/longhorn/dev/scale-test/scale-test.py

Purpose: development utility for generating many node-pinned StatefulSet manifests and watching pod, PVC, and VolumeAttachment events during Longhorn scale tests.

Important APIs/types/functions: constants configure namespace, node prefix/count, template, kubeconfig, and context. Functions `create_sts_deployment`, `create_sts_yaml`, `watch_pods_async`, `watch_pvc_async`, `watch_va_async`, and event processors use `kubernetes.client`, `config`, and `watch`.

Control flow: on startup it renders 100 StatefulSet YAML files under `out/`, loads kubeconfig, initializes logging and placeholder result maps, starts async watchers for pods, PVCs, and cluster volume attachments, and runs the event loop forever.

State and persistence: writes generated manifests to `out/sts<N>.yaml`. Runtime state is in-memory event processing maps that are currently unused placeholders.

Dependencies/integration points: depends on Python Kubernetes client, kubeconfig access, Kubernetes watch APIs, `StorageV1Api` volume attachments, and `statefulset.yaml` placeholders.

Risks/test signals: watchers are blocking iterators inside async tasks, generated files are relative to cwd, and TODO timing metrics are not implemented. Test signals are generated manifest count/content, kubeconfig loading, event logs during scaling, and eventual enhancement of PVC-to-pod/attachment timing maps.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/scale-test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/statefulset.yaml -->
# sources/control-plane/longhorn/dev/scale-test/statefulset.yaml

Purpose: template for scale-test StatefulSets, using placeholders to create one Longhorn-backed volume workload per target node.

Important APIs/types/functions: `apps/v1` `StatefulSet` with placeholders `@STS_NAME@` and `@NODE_NAME@`, node pinning via `spec.template.spec.nodeName`, BusyBox container, liveness probe on mounted path, and `volumeClaimTemplates` using StorageClass `longhorn`.

Control flow: `scale-test.py` substitutes placeholders into generated YAML. Replicas start at 0; `sample.sh` or manual scaling drives volume creation and attachment.

State and persistence: each generated StatefulSet creates a 1Gi RWO PVC per replica through Longhorn; pods write only probe-visible mount state.

Dependencies/integration points: depends on Longhorn default StorageClass, node names matching the configured prefix, StatefulSet controller, and kubelet volume attach/mount.

Risks/test signals: hard node pinning fails if node names differ, `busybox:latest` is mutable, and the liveness probe assumes mounted filesystem accessibility. Test signals are generated YAML validation, PVC creation, pod scheduling, Longhorn attach latency, and liveness stability.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/lm-update.sh -->
# sources/control-plane/longhorn/dev/scripts/lm-update.sh

Purpose: developer script for retagging the latest Longhorn manager image to a private DockerHub namespace, pushing it, patching local manager/driver manifests, and optionally recreating cluster resources.

Important APIs/types/functions: reads username and optional update flag, uses `${GOPATH}/src/github.com/longhorn/longhorn-manager`, `bin/latest_image`, `docker tag`, `docker push`, and multiple `sed -i` replacements against manager and driver YAML files.

Control flow: validates username, derives private image by replacing `longhornio` with username, pushes the tag, escapes slashes, rewrites image references and imagePullPolicy in two manifests, then deletes/recreates those manifests unless the second argument is non-empty.

State and persistence: mutates Docker registry state, local manifest files, and optionally live Kubernetes resources.

Dependencies/integration points: depends on GOPATH layout, Docker CLI credentials, `sed`, `kubectl`, and Longhorn manager deploy file paths in a separate repository.

Risks/test signals: regex replacement is broad, delete/create can disrupt running Longhorn, and it assumes old repository layout. Test signals are image push success, clean manifest diff, `kubectl apply --dry-run=server`, and rollout of manager/driver pods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/lm-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh -->
# sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh

Purpose: live-cluster helper that patches Longhorn DaemonSets and Deployments so their containers use `imagePullPolicy: Always`.

Important APIs/types/functions: namespace `longhorn-system`, kinds `daemonset deployments`, function `patch_kind`, `kubectl get <kind> -o name`, and strategic merge patch over `spec.template.spec.containers`.

Control flow: lists objects for each kind, derives container name from object name, applies a patch setting that container's pull policy to `Always`, then starts `kubectl get pods -w`.

State and persistence: mutates live workload pod templates, which triggers rollouts and changes future pod image pulling behavior.

Dependencies/integration points: depends on `kubectl`, current cluster permissions, object names matching container names, and Kubernetes patch semantics.

Risks/test signals: not every workload's container name necessarily equals object name; multi-container pods are only partially patched. Test signals are inspecting deployment/daemonset pod templates, rollout status, and pod image pull behavior after restart.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/install.sh -->
# sources/control-plane/longhorn/dev/upgrade-responder/install.sh

Purpose: end-to-end development installer for InfluxDB, Longhorn upgrade responder, and Grafana in a Kubernetes cluster.

Important APIs/types/functions: constants define repository, branch, generated values file, image, InfluxDB URL, app name, and timeouts. Functions `wait_for_deployment`, `install_influxdb`, `install_grafana`, `install_upgrade_responder`, and `output` orchestrate `kubectl`, `git clone`, `helm upgrade --install`, and status reporting.

Control flow: copies the current directory to a temporary directory, applies InfluxDB manifests and waits, writes a Helm values file with secrets/schema/release response/image, clones the upgrade responder repo, installs the chart, waits, installs Grafana, then prints service URLs and credentials, including a public IP fetched from `ifconfig.me`.

State and persistence: creates Kubernetes Secrets, PVCs, Deployments, Services, and a Helm release. Temporary files are removed on exit; generated values exist only in the temp directory.

Dependencies/integration points: depends on `kubectl`, `helm`, `git`, outbound network access, Longhorn StorageClass, InfluxDB, Grafana, Scarf URLs, and the upgrade responder chart.

Risks/test signals: embeds root/root and admin/admin demo credentials, uses external public IP lookup, and waits on `kubectl rollout status` without namespace flags. Test signals are Helm render/install success, deployment rollout, service reachability, InfluxDB database creation, and successful upgrade-check request ingestion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml -->
# sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml

Purpose: development Grafana deployment backed by Longhorn storage for visualizing upgrade responder data.

Important APIs/types/functions: creates a 2Gi `grafana-pvc`, an `apps/v1` Deployment using `grafana/grafana:7.1.0`, `GF_INSTALL_PLUGINS=grafana-worldmap-panel`, readiness/liveness probes, and a LoadBalancer Service on port 3000.

Control flow: Kubernetes binds the PVC through Longhorn, starts Grafana with persistent `/var/lib/grafana`, probes HTTP `/robots.txt` and TCP 3000, and exposes it through the LoadBalancer.

State and persistence: dashboard/configuration data persists in the Longhorn PVC. Pod runtime state is otherwise disposable.

Dependencies/integration points: depends on Longhorn StorageClass, Grafana image/plugin installation, LoadBalancer support, and the install script for rollout waiting.

Risks/test signals: old Grafana image and plugin install may have security or availability issues; LoadBalancer is environment-specific. Test signals are PVC binding, deployment readiness, service external address, plugin installation logs, and dashboard access.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml -->
# sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml

Purpose: development InfluxDB 1.8 deployment and service for upgrade responder telemetry.

Important APIs/types/functions: creates `influxdb-creds` Secret with base64 root credentials, a 2Gi Longhorn PVC, an `apps/v1` Deployment using `docker.io/influxdb:1.8.10`, and a ClusterIP Service on 8086.

Control flow: Kubernetes mounts the PVC at `/var/lib/influxdb`, injects credentials from the Secret, starts one InfluxDB replica, and exposes it internally as `influxdb.default.svc.cluster.local:8086`.

State and persistence: InfluxDB data persists in the Longhorn PVC; credentials persist in the Kubernetes Secret.

Dependencies/integration points: depends on Longhorn StorageClass, InfluxDB 1.x behavior, the upgrade responder values pointing at this service, and namespace `default`.

Risks/test signals: root/root credentials are demo-grade, no resource limits are set, and InfluxDB 1.8 is legacy. Test signals are PVC binding, pod readiness, service DNS, credential login, and upgrade responder writes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/block_volume.yaml -->
# sources/control-plane/longhorn/examples/block/block_volume.yaml

Purpose: demonstrates a Longhorn raw block PVC consumed directly by a pod as a block device.

Important APIs/types/functions: defines a `PersistentVolumeClaim` with `volumeMode: Block`, StorageClass `longhorn`, 2Gi size, and an nginx pod using `volumeDevices` with `devicePath: /dev/longhorn/testblk`.

Control flow: CSI provisions a block-mode Longhorn volume, Kubernetes attaches it to the pod, and kubelet exposes it as the configured device rather than mounting a filesystem.

State and persistence: block data persists in the PVC/Longhorn volume until claim deletion according to StorageClass reclaim policy.

Dependencies/integration points: depends on Longhorn CSI block volume support, RWO attach, kubelet block device mapping, and the default namespace.

Risks/test signals: applications must format/use the raw device correctly; deleting the PVC removes data if reclaim policy is Delete. Test signals are PVC bound, pod running, device present inside container, and read/write block tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/block_volume.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml

Purpose: example encrypted Longhorn raw block PVC consumed by a Deployment.

Important APIs/types/functions: creates block-mode PVC `longhorn-block-pvc` with StorageClass `longhorn-crypto-global`, then a single-replica `apps/v1` Deployment mounting it via `volumeDevices`.

Control flow: CSI validates crypto secrets from the StorageClass, provisions an encrypted block volume, and exposes the mapped block device to nginx at `/dev/longhorn/testblk`.

State and persistence: encrypted block data persists in the Longhorn volume; key material lives in the referenced `longhorn-crypto` Secret from companion manifests.

Dependencies/integration points: depends on Longhorn encryption support, dm-crypt/cryptsetup on nodes, CSI secret references, and `storageclass-crypto-global.yaml`.

Risks/test signals: missing or changed crypto secrets can prevent attach or make data inaccessible. Test signals are successful provisioning, node stage/publish events, device presence, and encrypted volume attach after pod restart.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/deployment_with_pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml

Purpose: global crypto Secret for block-mode encrypted Longhorn examples.

Important APIs/types/functions: Kubernetes `Secret` named `longhorn-crypto` in `longhorn-system` with `stringData` keys `CRYPTO_KEY_VALUE` and optional `CRYPTO_KEY_PROVIDER`.

Control flow: CSI secret references in encrypted StorageClasses resolve this Secret during provision/node stage/publish operations.

State and persistence: stores encryption passphrase material in Kubernetes Secret storage.

Dependencies/integration points: depends on Kubernetes Secret access by Longhorn CSI components and matching StorageClass secret names/namespaces.

Risks/test signals: example passphrase is insecure and rotation affects volume accessibility. Test signals are secret existence, CSI permission to read it, and successful encrypted block volume provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/secret-crypto-global.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml

Purpose: StorageClass for globally keyed encrypted Longhorn block volumes.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass` named `longhorn-crypto-global`, provisioner `driver.longhorn.io`, `allowVolumeExpansion: true`, `encrypted: "true"`, replica/timeout/fromBackup parameters, and CSI provisioner/node-publish/node-stage secret references.

Control flow: PVCs using this class trigger Longhorn CSI provisioning with encryption enabled and early secret validation. Node operations retrieve the same global Secret from `longhorn-system`.

State and persistence: class itself has no data; it controls encrypted Longhorn volume creation and secret lookup.

Dependencies/integration points: depends on `longhorn-crypto` Secret, CSI external provisioner/node plugins, and node crypto tooling.

Risks/test signals: all volumes share one passphrase in this example. Online expansion secret references are commented and require feature gates if enabled. Test signals are StorageClass validation, PVC provisioning, attach/mount, and expansion behavior if enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/crypto/storageclass-crypto-global.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml

Purpose: FIPS/RHEL-oriented crypto Secret example for encrypted Longhorn volumes.

Important APIs/types/functions: Secret `longhorn-crypto` includes passphrase/provider plus cipher `aes-cbc-essiv:sha256`, hash `sha256`, key size `256`, and PBKDF `pbkdf2`; optional PBKDF iteration and memory settings are documented.

Control flow: CSI encryption operations consume these keys to configure cryptsetup in a FIPS-compatible way, avoiding non-FIPS KDFs.

State and persistence: stores encryption parameters and passphrase in Kubernetes Secret storage.

Dependencies/integration points: depends on Longhorn encrypted volume support, node cryptsetup behavior on RHEL/FIPS systems, and StorageClass secret references.

Risks/test signals: wrong cipher/KDF choices can fail attach or violate FIPS expectations; example passphrase is not production-safe. Test signals are successful encrypted volume creation on FIPS nodes, cryptsetup compatibility, and attach after node reboot.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized-rhel-FIPS-enabled.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml

Purpose: customized crypto Secret example for encrypted Longhorn volumes using explicit cipher, hash, size, and PBKDF.

Important APIs/types/functions: Secret keys include `CRYPTO_KEY_VALUE`, `CRYPTO_KEY_PROVIDER`, `CRYPTO_KEY_CIPHER: aes-xts-plain64`, `CRYPTO_KEY_HASH: sha256`, `CRYPTO_KEY_SIZE: 256`, and `CRYPTO_PBKDF: argon2i`.

Control flow: Longhorn CSI reads these values during encrypted volume operations and passes them to the node crypto stack.

State and persistence: persists key configuration and passphrase in Kubernetes Secret storage.

Dependencies/integration points: depends on cryptsetup support for the selected cipher and PBKDF on all target nodes.

Risks/test signals: heterogeneous node crypto versions can make argon2i or cipher handling inconsistent. Test signals are encrypted PVC provisioning, node-stage logs, and cross-node attach tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-customized.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml

Purpose: basic global crypto Secret for encrypted filesystem-volume examples.

Important APIs/types/functions: Kubernetes Secret `longhorn-crypto` in `longhorn-system` with passphrase `CRYPTO_KEY_VALUE` and provider `CRYPTO_KEY_PROVIDER`.

Control flow: encrypted StorageClasses reference this Secret for CSI provision, node stage, and node publish operations.

State and persistence: Kubernetes stores the passphrase; encrypted Longhorn volumes depend on it for access.

Dependencies/integration points: integrates with Longhorn CSI and encrypted StorageClass examples.

Risks/test signals: static shared passphrase is only an example. Test signals are secret readability by CSI and successful encrypted PVC lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/secret-crypto-global.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml

Purpose: encrypted Longhorn StorageClass using a single global Secret in `longhorn-system`.

Important APIs/types/functions: `StorageClass` `longhorn-crypto-global`, provisioner `driver.longhorn.io`, expansion enabled, `encrypted: "true"`, replica/timeout/fromBackup parameters, and CSI secret parameters for provisioner, node publish, and node stage.

Control flow: PVC creation invokes Longhorn CSI with encryption enabled and secret checks; node staging/publishing uses the global Secret to unlock the volume.

State and persistence: controls encrypted volume provisioning; stores no runtime data itself.

Dependencies/integration points: depends on companion `longhorn-crypto` Secret and CSI secret parameter substitution.

Risks/test signals: global key blast radius is high. Test signals are provisioning failure when Secret is absent, success when present, mount after restart, and optional expansion tests with node-expand secrets if feature gates are enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-global.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml

Purpose: encrypted StorageClass pattern where each PVC uses a Secret named after the PVC, stored in `longhorn-system`.

Important APIs/types/functions: StorageClass `longhorn-secure-per-volume-ns-longhorn-system` uses `${pvc.name}` for CSI secret names and fixed secret namespace `longhorn-system`.

Control flow: CSI parameter substitution resolves each PVC's name to a Secret and uses that Secret for provision/node operations.

State and persistence: class defines lookup convention only; per-volume secrets and Longhorn volumes carry persistent state.

Dependencies/integration points: depends on PVC-name-based Secrets pre-created in `longhorn-system`, Longhorn CSI token substitution, and encryption tooling.

Risks/test signals: PVC names must be valid Secret names and must not collide across namespaces if centralized in `longhorn-system`. Test signals are per-PVC secret creation, provisioning success, attach in source namespace, and failure modes for missing secret.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume-dedicated-namespace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml -->
# sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml

Purpose: encrypted StorageClass pattern where each PVC references a same-namespace Secret named after the PVC.

Important APIs/types/functions: StorageClass `longhorn-crypto-per-volume` uses `${pvc.name}` and `${pvc.namespace}` in CSI secret parameters for provisioner, node publish, and node stage.

Control flow: on PVC creation, CSI resolves the Secret in the claim namespace, enabling per-volume/per-namespace key isolation.

State and persistence: class stores policy; each namespace stores its own Secret and Longhorn stores encrypted volume data.

Dependencies/integration points: depends on Kubernetes CSI secret template substitution, namespace-local Secret management, and Longhorn encryption.

Risks/test signals: Secret lifecycle must be coordinated with PVC lifecycle; deleting the Secret can make data inaccessible. Test signals are provisioning with namespace-local Secret, cross-namespace isolation, and attach after pod reschedule.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/crypto/storageclass-crypto-per-volume.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/csi/example_pv.yaml -->
# sources/control-plane/longhorn/examples/csi/example_pv.yaml

Purpose: static CSI PersistentVolume example binding an existing Longhorn volume to a PVC and pod.

Important APIs/types/functions: defines `PersistentVolume` with CSI driver `driver.longhorn.io`, `volumeHandle: existing-longhorn-volume`, fsType `ext4`, volume attributes, a bound PVC using `volumeName`, and an nginx pod mounting `/data`.

Control flow: Kubernetes binds the PVC to the static PV, CSI attaches/mounts the existing Longhorn volume, and the pod liveness probe checks `/data/lost+found`.

State and persistence: existing Longhorn volume data is exposed through the PV; reclaim policy is Delete in this example.

Dependencies/integration points: depends on a pre-existing Longhorn volume named by `volumeHandle`, CSI attach/mount, and ext4 filesystem.

Risks/test signals: wrong handle or filesystem causes mount failures; Delete reclaim can remove an existing volume unexpectedly. Test signals are PV/PVC bound state, pod mount success, and Longhorn UI/API volume association.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/csi/example_pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/data_migration.yaml -->
# sources/control-plane/longhorn/examples/data_migration.yaml

Purpose: one-shot Job for copying data from one PVC to another.

Important APIs/types/functions: `batch/v1` Job `volume-migration`, one completion, `backoffLimit: 3`, container `registry.suse.com/bci/golang:1.24`, command `cp -r -v /mnt/old/. /mnt/new`, and two PVC volumes.

Control flow: Kubernetes mounts source and target PVCs, runs the copy command once, and marks the Job complete or retries on failure.

State and persistence: mutates target PVC contents; source PVC is read/write mounted by default and not explicitly protected.

Dependencies/integration points: depends on both PVCs being in the selected namespace and attachable to the same pod/node under their access modes.

Risks/test signals: `cp -r` may not preserve all metadata, sparse files, hard links, ownership, or live-write consistency. Test signals are Job completion, copied file counts/checksums, application quiescence, and target workload validation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/data_migration.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/deployment.yaml -->
# sources/control-plane/longhorn/examples/deployment.yaml

Purpose: MySQL Deployment example using a Longhorn RWO PVC.

Important APIs/types/functions: headless-style Service `mysql` with `clusterIP: None`, PVC `mysql-pvc`, and Deployment `mysql` with Recreate strategy, `mysql:5.6`, root password env var, port 3306, and liveness probe on `/var/lib/mysql/lost+found`.

Control flow: CSI provisions the PVC, Deployment creates one MySQL pod, kubelet mounts the volume, and the liveness probe checks filesystem mount availability.

State and persistence: MySQL data persists in the Longhorn PVC.

Dependencies/integration points: depends on Longhorn StorageClass, MySQL image behavior, RWO scheduling, and Kubernetes Service discovery.

Risks/test signals: password is hard-coded, MySQL 5.6 is obsolete, and liveness probe tests only mount presence. Test signals are PVC bound, MySQL readiness/application checks, data persistence across pod recreation, and backup/snapshot coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn backing image data source pods.

Important APIs/types/functions: selects pods with `longhorn.io/component: backing-image-data-source` and allows ingress from manager, instance manager, backing image manager, and other backing image data source pods.

Control flow: once applied in a policy-enforcing CNI, only matching peer pods can initiate ingress to selected data source pods.

State and persistence: stores network policy state in Kubernetes; no data persistence.

Dependencies/integration points: depends on labels emitted by Longhorn runtime pods and a CNI that enforces `networking.k8s.io/v1` policies.

Risks/test signals: missing required egress or external download allowances may still block workflows depending on cluster default policies. Test signals are backing image download/upload/clone flows and connectivity from each allowed component.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml

Purpose: ingress NetworkPolicy restricting Longhorn backing image manager pods.

Important APIs/types/functions: selects `longhorn.io/component: backing-image-manager` and allows ingress from manager, instance manager, and backing image manager pods.

Control flow: policy-enforcing CNIs admit only selected peer pods to backing image manager pods.

State and persistence: only Kubernetes NetworkPolicy state.

Dependencies/integration points: depends on Longhorn backing image manager labels and CNI policy support.

Risks/test signals: incomplete peer list can break backing image synchronization. Test signals are backing image create, sync, transfer, and manager-to-manager connectivity checks.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml -->
# sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml

Purpose: ingress NetworkPolicy for Longhorn instance manager pods.

Important APIs/types/functions: selects `longhorn.io/component: instance-manager` and allows ingress from manager, other instance managers, and backing image data source pods.

Control flow: restricts inbound traffic to the data-plane manager pods while preserving Longhorn control/data communications between allowed components.

State and persistence: Kubernetes policy object only.

Dependencies/integration points: depends on CNI enforcement and Longhorn runtime pod labels.

Risks/test signals: data engine communication paths are sensitive; an omitted peer can break attach, rebuild, or replica traffic. Test signals are volume attach, replica rebuild, engine/replica instance health, and backing image interactions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn manager pods.

Important APIs/types/functions: selects `app: longhorn-manager` and allows ingress from manager, UI, CSI plugin, recurring-job-managed pods, job-task pods, and driver deployer pods.

Control flow: limits access to the manager API/service to known Longhorn components in `longhorn-system`.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on labels for Longhorn UI, CSI, jobs, recurring jobs, and deployer, plus CNI enforcement.

Risks/test signals: external clients, ingress, monitoring, or support tooling may be blocked unless separately allowed. Test signals are UI access to backend, CSI provisioning calls, recurring jobs, driver deployment, and manager peer communication.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn recovery backend pods.

Important APIs/types/functions: selects `longhorn.io/recovery-backend: longhorn-recovery-backend` and allows TCP port 9503 ingress without a `from` selector.

Control flow: policy allows any source to reach port 9503 on selected pods, while other ports are isolated if ingress isolation applies.

State and persistence: Kubernetes policy only.

Dependencies/integration points: depends on recovery backend labels, service port 9503, and CNI behavior.

Risks/test signals: open source scope may be broader than desired; tightening requires knowing all recovery clients. Test signals are recovery workflow connectivity and port-scoped network probes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml

Purpose: ingress NetworkPolicy allowing Longhorn UI traffic from an ingress-nginx controller.

Important APIs/types/functions: selects `app: longhorn-ui` and allows ingress from namespace label `kubernetes.io/metadata.name: ingress-nginx` plus ingress-nginx controller pod labels.

Control flow: with a policy CNI, only matching ingress controller pods can initiate traffic to UI pods.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on ingress-nginx namespace/pod labels matching the example and on a separate Ingress/Service exposing the UI.

Risks/test signals: different ingress controllers or labels require changes; direct cluster access may be blocked. Test signals are UI reachability through ingress and denied direct pod/service access where expected.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml

Purpose: ingress NetworkPolicy for the Longhorn admission webhook endpoint.

Important APIs/types/functions: selects `longhorn.io/admission-webhook: longhorn-admission-webhook` and allows TCP port 9502 ingress without restricting source.

Control flow: Kubernetes API server or other clients can reach webhook port 9502 while other ports are isolated under ingress policy.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on webhook pod labels, webhook Service, admissionregistration configuration, and CNI support.

Risks/test signals: source unrestricted is permissive, but API server source selection is CNI/environment-specific. Test signals are admission webhook calls during Longhorn CR changes and port 9502 connectivity from API server path.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_gev.yaml -->
# sources/control-plane/longhorn/examples/pod_with_gev.yaml

Purpose: example pod using a Generic Ephemeral Volume backed by Longhorn.

Important APIs/types/functions: Pod `volume-test` defines `volumes[].ephemeral.volumeClaimTemplate` with RWO Longhorn storage request, mounts it at `/data`, and probes `/data/lost+found`.

Control flow: Kubernetes creates an ephemeral PVC for the pod, Longhorn provisions the volume, kubelet mounts it, and deletion of the pod triggers cleanup according to ephemeral volume ownership.

State and persistence: data is tied to the pod lifecycle rather than a user-managed PVC.

Dependencies/integration points: depends on Kubernetes generic ephemeral volume support and Longhorn dynamic provisioning.

Risks/test signals: data is not durable beyond pod lifecycle. Test signals are ephemeral PVC creation/owner references, pod mount success, and cleanup after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_gev.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/pod_with_pvc.yaml

Purpose: basic pod plus PVC example for a Longhorn filesystem volume.

Important APIs/types/functions: PVC `longhorn-volv-pvc` requests 2Gi RWO storage from `longhorn`; pod `volume-test` mounts it at `/data` and probes `/data/lost+found`.

Control flow: Longhorn provisions the PVC, Kubernetes schedules the pod, attaches/mounts the volume, and the liveness probe verifies mount presence.

State and persistence: filesystem data persists in the PVC across pod restarts/deletion.

Dependencies/integration points: depends on Longhorn StorageClass and kubelet CSI mount.

Risks/test signals: liveness only checks filesystem scaffold, not application IO. Test signals are PVC bound, pod running, data write/read after pod recreation, and volume detach on pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml -->
# sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml

Purpose: ReadWriteMany Longhorn example with three pods sharing an RWX PVC.

Important APIs/types/functions: Service `rwx-test`, PVC `rwx-test` with `ReadWriteMany`, Deployment with three replicas and Recreate strategy, an Ubuntu writer container appending dates to `/data/index.html`, and an nginx container serving the same data.

Control flow: Longhorn creates an RWX/share-manager backed volume, all replicas mount the shared filesystem, writer updates content, and nginx serves it.

State and persistence: shared file data persists in the Longhorn RWX volume.

Dependencies/integration points: depends on Longhorn RWX/NFS share manager, multi-attach support, and pod scheduling across nodes.

Risks/test signals: concurrent writes are simplistic and may hide real application locking needs. Test signals are three pods running, shared updates visible from all pods, share manager health, and service HTTP responses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/rwx-nginx-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml -->
# sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml

Purpose: StorageClass enabling Longhorn migratable volumes.

Important APIs/types/functions: StorageClass `longhorn-migratable`, provisioner `driver.longhorn.io`, expansion enabled, replica/timeout/fromBackup parameters, and `migratable: "true"`.

Control flow: PVCs using this class create Longhorn volumes marked for migration/live-migration capable behavior.

State and persistence: StorageClass policy influences Longhorn volume spec; volume data persists in created PVCs.

Dependencies/integration points: depends on Longhorn migration support and consumer workloads that use compatible attach semantics.

Risks/test signals: migratable behavior has scheduling and attachment constraints; not every workload should use it. Test signals are PVC provisioning, migration workflow, attach/detach events, and workload continuity during migration.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/rwx/storageclass-migratable.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pod.yaml -->
# sources/control-plane/longhorn/examples/simple_pod.yaml

Purpose: simple consumer pod for the companion Longhorn PVC example.

Important APIs/types/functions: Pod `longhorn-simple-pod` mounts PVC `longhorn-simple-pvc` at `/data`, uses nginx stable-alpine, and probes `/data/lost+found`.

Control flow: once the PVC exists and is bound, kubelet attaches/mounts it into the pod and liveness checks the mounted filesystem.

State and persistence: data persists in `longhorn-simple-pvc`.

Dependencies/integration points: depends on companion PVC, Longhorn CSI, and default namespace.

Risks/test signals: pod fails until PVC exists; probe is mount-only. Test signals are PVC binding, pod running, mount path visibility, and persistence after pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pvc.yaml -->
# sources/control-plane/longhorn/examples/simple_pvc.yaml

Purpose: minimal Longhorn PVC example.

Important APIs/types/functions: `PersistentVolumeClaim` `longhorn-simple-pvc` in `default`, RWO access mode, StorageClass `longhorn`, and 1Gi request.

Control flow: applying the manifest triggers dynamic provisioning through Longhorn CSI.

State and persistence: creates a persistent Longhorn volume governed by the StorageClass reclaim policy.

Dependencies/integration points: depends on installed Longhorn CSI provisioner and StorageClass `longhorn`.

Risks/test signals: default reclaim behavior may delete data with PVC deletion. Test signals are PVC Bound, PV creation, Longhorn volume creation, and successful pod consumption.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml -->
# sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml

Purpose: VolumeSnapshotContent example that imports an existing Longhorn backup as a CSI snapshot content object.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent`, driver `driver.longhorn.io`, class `longhorn`, `deletionPolicy: Delete`, `source.snapshotHandle: bs://...`, and `volumeSnapshotRef`.

Control flow: snapshot controller binds this content to the referenced VolumeSnapshot, allowing restore PVCs to use the backup-backed snapshot.

State and persistence: references external backupstore data through the snapshot handle; Kubernetes stores snapshot binding state.

Dependencies/integration points: depends on CSI snapshot CRDs/controller, Longhorn snapshotter, and a valid backupstore URL.

Risks/test signals: placeholder backup handle must be changed; Delete policy may remove snapshot content metadata or backend data depending on driver behavior. Test signals are bound VolumeSnapshotContent, snapshot ready status, and restore PVC success.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/existing_backup.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml -->
# sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml

Purpose: PVC restore example using a VolumeSnapshot that represents an existing Longhorn backup.

Important APIs/types/functions: PVC `test-restore-existing-backup` uses `dataSource` pointing to `VolumeSnapshot test-snapshot-existing-backup`, StorageClass `longhorn`, RWO, and 2Gi request.

Control flow: CSI provisioner creates a new Longhorn volume from the snapshot/backup data source.

State and persistence: restored data persists in the new PVC/Longhorn volume.

Dependencies/integration points: depends on snapshot content and snapshot object being ready, Longhorn backupstore access, and CSI data source support.

Risks/test signals: requested size must be sufficient for restore; missing backupstore credentials break provisioning. Test signals are PVC Bound, Longhorn restore progress, and data validation in a consumer pod.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_existing_backup.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml -->
# sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml

Purpose: PVC restore example from a Longhorn VolumeSnapshot created from another PVC.

Important APIs/types/functions: PVC `test-restore-snapshot-pvc` uses `dataSource` referencing `VolumeSnapshot test-snapshot-pvc`.

Control flow: once the source snapshot is ready, CSI provisions a new Longhorn volume from that snapshot.

State and persistence: restored filesystem/block contents persist in the new PVC.

Dependencies/integration points: depends on CSI snapshot controller, Longhorn snapshotter, source snapshot readiness, and StorageClass `longhorn`.

Risks/test signals: restore size must be valid and source snapshot must not be deleted prematurely. Test signals are snapshot `readyToUse`, PVC Bound, and restored data checks.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/restore_pvc_snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml

Purpose: VolumeSnapshot object that binds to pre-created VolumeSnapshotContent for an existing backup.

Important APIs/types/functions: `VolumeSnapshot` `test-snapshot-existing-backup`, class `longhorn`, source `volumeSnapshotContentName: test-existing-backup`.

Control flow: snapshot controller binds the snapshot to named content rather than creating a new snapshot from a PVC.

State and persistence: stores Kubernetes snapshot object state; actual data remains in the referenced backupstore.

Dependencies/integration points: depends on `existing_backup.yaml` content and CSI snapshot CRDs/controller.

Risks/test signals: names and namespace must match the content's `volumeSnapshotRef`. Test signals are bound snapshot, ready status, and restore PVC success.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_existing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml

Purpose: VolumeSnapshot example that snapshots an existing PVC.

Important APIs/types/functions: `VolumeSnapshot` `test-snapshot-pvc`, class `longhorn`, source `persistentVolumeClaimName: test-vol`.

Control flow: snapshot controller calls Longhorn CSI snapshotter to create a point-in-time snapshot of the named PVC.

State and persistence: snapshot metadata persists in Kubernetes and Longhorn; data is retained according to snapshot class deletion policy and Longhorn behavior.

Dependencies/integration points: depends on source PVC `test-vol`, CSI snapshot controller, VolumeSnapshotClass `longhorn`, and Longhorn snapshot APIs.

Risks/test signals: source PVC must exist and be in a suitable state. Test signals are VolumeSnapshot ready status, VolumeSnapshotContent creation, and restore test.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshot_pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml -->
# sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml

Purpose: VolumeSnapshotClass for Longhorn CSI snapshots.

Important APIs/types/functions: `VolumeSnapshotClass` named `longhorn`, driver `driver.longhorn.io`, `deletionPolicy: Delete`, with commented CSI snapshotter secret parameters.

Control flow: VolumeSnapshot objects referencing this class route snapshot operations to the Longhorn CSI driver.

State and persistence: class controls snapshot lifecycle behavior but stores no data.

Dependencies/integration points: depends on external snapshotter CRDs/controller and Longhorn CSI snapshot support.

Risks/test signals: Delete policy removes snapshots when snapshot objects are deleted; secret parameters may be required for secured setups. Test signals are snapshot creation/deletion and restore from snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/snapshot/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/statefulset.yaml -->
# sources/control-plane/longhorn/examples/statefulset.yaml

Purpose: StatefulSet example where each nginx replica gets its own Longhorn PVC.

Important APIs/types/functions: NodePort Service `nginx`, StatefulSet `web` with two replicas, `registry.k8s.io/nginx-slim:0.8`, liveness probe on mounted path, and `volumeClaimTemplates` requesting 1Gi RWO Longhorn volumes.

Control flow: StatefulSet controller creates stable pod identities and per-replica PVCs; Longhorn provisions and attaches each volume.

State and persistence: each replica's web data persists in its own PVC.

Dependencies/integration points: depends on Longhorn StorageClass, StatefulSet volume claim templates, and NodePort service exposure.

Risks/test signals: old image and NodePort exposure are example-only. Test signals are two PVCs bound, ordered pod startup, volume persistence per ordinal, and service reachability.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/storageclass.yaml -->
# sources/control-plane/longhorn/examples/storageclass.yaml

Purpose: sample Longhorn StorageClass showing common and optional parameters.

Important APIs/types/functions: StorageClass `longhorn-test`, provisioner `driver.longhorn.io`, expansion enabled, reclaim Delete, Immediate binding, replica/timeout/fromBackup/fsType parameters, and commented examples for mkfs, backing images, selectors, recurring jobs, unmap, and NFS options.

Control flow: PVCs using this class are dynamically provisioned by Longhorn CSI with supplied parameters.

State and persistence: controls volume spec defaults; created volumes persist through PVC/PV lifecycle.

Dependencies/integration points: depends on Longhorn CSI parameter support and optional backing image/recurring job features when uncommented.

Risks/test signals: Immediate binding can provision before pod scheduling constraints are known; optional JSON/string parameters are easy to mistype. Test signals are StorageClass admission, PVC provisioning, parameter reflection in Longhorn Volume spec, and expansion/reclaim behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml

Purpose: pod plus PVC example using Longhorn v2 data engine StorageClass.

Important APIs/types/functions: PVC `longhorn-volv-pvc` requests 2Gi from `longhorn-v2-data-engine`; pod `volume-test` mounts it at `/data` and probes `/data/lost+found`.

Control flow: Longhorn provisions a v2 data engine volume, Kubernetes attaches/mounts it, and the pod validates mount presence through liveness.

State and persistence: data persists in the v2 Longhorn volume.

Dependencies/integration points: depends on v2 data engine being enabled/supported on the cluster, v2 StorageClass, and node prerequisites.

Risks/test signals: v2 data engine has different node/kernel/SPDK-style prerequisites than v1. Test signals are PVC Bound, Longhorn Volume `dataEngine: v2`, attach/mount success, and workload IO.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/storageclass.yaml -->
# sources/control-plane/longhorn/examples/v2/storageclass.yaml

Purpose: StorageClass for Longhorn v2 data engine volumes.

Important APIs/types/functions: StorageClass `longhorn-v2-data-engine`, provisioner `driver.longhorn.io`, expansion enabled, Delete reclaim, Immediate binding, replica/timeout/fsType, and `dataEngine: "v2"`; comments show optional selectors, recurring jobs, backup, backing image, unmap, and NFS options.

Control flow: PVCs using this class request Longhorn v2 data engine provisioning through CSI.

State and persistence: StorageClass policy influences Longhorn Volume specs and created volume data persists in Longhorn.

Dependencies/integration points: depends on Longhorn v2 engine support, compatible nodes, and CSI parameter handling.

Risks/test signals: applying this class where v2 is disabled or prerequisites are missing causes provisioning/attach failures. Test signals are PVC provisioning, Volume CR dataEngine, instance manager/v2 frontend health, and IO/expansion tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/renovate.json -->
# sources/control-plane/longhorn/renovate.json

Purpose: repository Renovate configuration inheritance.

Important APIs/types/functions: JSON object with `extends: ["github>longhorn/release:renovate-default"]`.

Control flow: Renovate loads this config, resolves the shared Longhorn release preset from GitHub, and applies preset rules for dependency update discovery and PR creation.

State and persistence: no runtime state; Renovate creates update branches/PRs externally when run.

Dependencies/integration points: depends on Renovate, GitHub preset resolution, and the `longhorn/release` repository.

Risks/test signals: shared preset changes affect this repo without local diff, and unavailable GitHub preset resolution breaks Renovate. Test signals are `renovate-config-validator`, dry-run logs showing loaded preset, and expected dependency update PR behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/renovate.json -->
