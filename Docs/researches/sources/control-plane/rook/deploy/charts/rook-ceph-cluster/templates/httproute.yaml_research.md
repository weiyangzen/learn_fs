## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/httproute.yaml

Purpose: renders a Gateway API HTTPRoute for the Ceph dashboard when `.Values.route.dashboard.host` is configured.

Important template behavior: creates `HTTPRoute` named `<clusterName>-dashboard`, applies optional labels/annotations, sets hostnames, parentRefs, backend service `rook-ceph-mgr-dashboard`, port from explicit dashboard port or defaults to 8443 for SSL and 7000 for non-SSL, and path match from values.

Control flow: single conditional around dashboard route host presence.

State and persistence: exposes the mgr dashboard through Gateway API. It does not enable the dashboard; that comes from CephCluster spec.

Dependencies and integration points: requires Gateway API CRDs/controller and Rook-created dashboard service. Risks: backend TLS expectations are not encoded in HTTPRoute; wrong port defaults or parentRefs break routing; exposing dashboard should be paired with auth/TLS policy. Tests should render with SSL and non-SSL dashboard settings.
