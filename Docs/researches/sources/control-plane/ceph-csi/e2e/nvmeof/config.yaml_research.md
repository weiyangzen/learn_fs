# sources/control-plane/ceph-csi/e2e/nvmeof/config.yaml

Purpose: defines the ConfigMap consumed by the temporary NVMe-oF gateway deployment. Its `config` key is a full `ceph-nvmeof.conf` template with Kubernetes placeholders for pod name, ANA group, and pod IP.

Important APIs/types/functions: the Kubernetes resource is a `v1 ConfigMap` named `ceph-nvmeof-config` labeled `app=ceph-nvmeof-gateway`. The embedded configuration includes sections `[gateway]`, `[gateway-logs]`, `[discovery]`, `[ceph]`, `[mtls]`, `[spdk]`, and `[monitor]`.

Control flow: `deployment.yaml` mounts this ConfigMap at `/config`; the init container runs `sed` to replace `@@POD_NAME@@`, `@@ANA_GROUP@@`, and `@@POD_IP@@`, producing `/etc/ceph/nvmeof.conf`. The gateway container then starts with `-c /etc/ceph/nvmeof.conf`.

State and persistence: stores gateway runtime configuration in Kubernetes. The config points the gateway at `nvmeofpool`, disables auth, disables strict listener IP verification, enables state update notifications, sets debug logging, sets discovery to `0.0.0.0:8009`, and configures SPDK memory/tgt path/timeouts.

Dependencies and integration points: mounted by the gateway Deployment, paired with Ceph monitor/keyring data from Rook Secrets, and coordinated with the pool and listener values injected into NVMe-oF CSI StorageClasses.

Risks: many values are test-static (`nvmeofpool`, admin Ceph ID, auth disabled, fixed ports, `verify_listener_ip=False`). Config comments note TODOs for dynamic name/group/address and service behavior. Drift between this config and StorageClass listener/gateway parameters can break provisioning.

Test signals: init container successfully renders the config, `ceph nvme-gw create/show` succeeds, the gateway starts, and CSI can create NVMe-oF-backed volumes through the configured listener.
