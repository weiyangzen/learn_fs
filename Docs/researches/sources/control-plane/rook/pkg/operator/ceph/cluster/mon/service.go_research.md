# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service.go

## Purpose
This file creates and exports Kubernetes Services for Ceph monitors. Monitor services provide stable ClusterIPs for monitor endpoints and optional multicluster exported addresses.

## Important APIs, Types, And Functions
`(c *Cluster) createService(mon *monConfig)` builds a `v1.Service` named after the monitor resource with labels from `c.getLabels()`, selector labels for the monitor pod, and one or two TCP service ports. `addServicePort()` from `util.go` is used for msgr1 and msgr2. `(c *Cluster) exportService(service *v1.Service, monDaemon string)` exports the service through `k8sutil.ExportService()` and removes monitor canary deployments afterward.

## Control Flow And State
`createService` sets an owner reference, adds msgr1 only when the monitor's configured port is not the default msgr2 port, always adds msgr2, and optionally pins `Spec.ClusterIP` to `mon.PublicIP` when a service is missing. This supports disaster recovery when a service was deleted but monitor endpoint state still knows the expected ClusterIP. It then calls `k8sutil.CreateOrUpdateService`. If the resulting service is nil, it logs an error and returns nil without a Kubernetes object. `exportService` defers canary cleanup until after export because multicluster DNS may require the canary pod to be running.

## Dependencies And Integration Points
The code depends on Kubernetes Services, Rook owner references, monitor labels, Rook service create/update helpers, Kubernetes API error classification, and multicluster service export. It integrates with monitor deployment startup and disaster recovery endpoint preservation.

## Risks And Test Signals
The critical risk is accidentally changing an existing ClusterIP, which Kubernetes does not allow and which would break monitor endpoints. The code only sets `ClusterIP` when the service is not found. `service_test.go` covers the disaster recovery path: existing services are not overwritten, but after deletion the expected public IP is assigned as the service ClusterIP.
