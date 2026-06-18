<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml

Purpose: exposes the Ceph manager dashboard HTTPS endpoint through a cloud/load-balancer Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-loadbalancer`, port/targetPort `8443`, active mgr selector labels, and `type: LoadBalancer`.
Control flow: Kubernetes/cloud controller allocates an external load balancer and routes it to the active mgr dashboard endpoint. State includes Service status load-balancer ingress and endpoint slices. Dependencies are cloud/load balancer support, dashboard HTTPS, and Rook mgr labels. Risks: public exposure of an administrative dashboard, cloud firewall defaults, self-signed certificates, and endpoint churn on mgr failover. Test signals: external IP assigned, endpoints point at active mgr, HTTPS dashboard reachable, and failover maintains routing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml -->
