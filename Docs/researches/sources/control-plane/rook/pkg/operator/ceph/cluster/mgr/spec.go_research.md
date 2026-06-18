# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec.go

## Purpose

This file builds Kubernetes Deployments, containers, labels, annotations, and Services for Ceph manager daemons. It encodes how the mgr daemon, active-manager sidecar, Multus command-proxy sidecar, metrics service, and dashboard service should look from a `CephCluster` spec.

## Important APIs and Control Flow

`makeDeployment()` constructs the mgr Deployment and pod template. It starts with daemon volumes and a chown init container, adds the main `ceph-mgr` container, applies placement, tolerations, priority class, annotations, labels, owner references, and Ceph/Rook version labels. When `Mgr.Count > 1`, it adds the `watch-active` sidecar, config/secret volumes, and anti-affinity across hostnames or required zones. When log collection is enabled it adds the log collector and shares the process namespace. Host networking sets DNS policy; Multus applies network annotations, mounts the admin keyring, and adds a command-proxy sidecar.

`makeMgrDaemonContainer()` configures the `ceph-mgr` command, daemon flags, `client-mount-uid/gid`, foreground mode, ports for daemon traffic, metrics, and dashboard, standard daemon env vars, orchestrator-module env vars, resources, security context, and probes. Non-host-network pods advertise `ROOK_POD_IP` as public address.

`makeMgrSidecarContainer()` builds the Rook `ceph mgr watch-active` sidecar that can update active/standby labels and carries cluster, namespace, dashboard, monitoring, endpoint, and Ceph version env vars. `makeCmdProxySidecarContainer()` supports Multus command execution through admin keyring and `CEPH_ARGS`.

`MakeMetricsService()` and `makeDashboardService()` build ClusterIP services. Metrics selectors target `mgr_role=active`, except the external manager service intentionally has no selector. Dashboard service names and ports reflect SSL and dashboard spec settings.

## State, Persistence, and Dependencies

This file does not write objects directly; callers create or update the generated Deployment/Service objects. Persistent state is encoded as Kubernetes metadata and pod template spec. Dependencies include Rook controller helpers for daemon volumes, probes, resources, labels, Multus, keyrings, and owner references, plus Kubernetes apps/core API types.

## Risks and Test Signals

Selector changes can route metrics/dashboard traffic incorrectly, so `buildSelectorLabels()` and active labels are high-risk. Network transitions are also sensitive: host networking changes public address behavior, while Multus requires extra keyring volume and command proxy. `spec_test.go` covers pod shape, Multus, probes, services, host networking, annotations, and manager-specific host-network override behavior; `mgr_test.go` covers service selector migration and active labels.
