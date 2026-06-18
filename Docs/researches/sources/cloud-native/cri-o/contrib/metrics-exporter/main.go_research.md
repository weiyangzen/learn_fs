# sources/cloud-native/cri-o/contrib/metrics-exporter/main.go

## Purpose
In-cluster Go HTTP proxy that discovers Kubernetes nodes, writes Prometheus scrape config, and proxies per-node CRI-O metrics endpoints.

## Important APIs, Types, and Functions
main calls run. run builds in-cluster client, lists nodes, registers http.Handle("/nodeName") per node, generates jobConfig YAML, creates or updates a ConfigMap key config, and listens on :8080. handler.ServeHTTP builds http://nodeIP:CRIO_METRICS_PORT/metrics and copies 200 responses.

## Control Flow
Startup is one-shot discovery/config generation followed by serving HTTP. Each request proxies synchronously to a node CRI-O metrics endpoint using request context; non-200 status is propagated and transport/read/write errors are logged.

## State and Persistence
Kubernetes ConfigMap is persistent state. Process keeps node handlers in global http.DefaultServeMux; node list is not refreshed after startup.

## Dependencies
Depends on client-go in-cluster config, env.Default helper, logrus, net/http, Kubernetes nodes API, ConfigMaps API, and CRI-O metrics port default 9090.

## Integration Points
Runs under cluster.yaml service account/RBAC and service; Prometheus can scrape service paths created in ConfigMap.

## Risks and Edge Cases
Uses node.Status.Addresses[0] without type or length checks; startup fails outside cluster; config update treats any Get error as create path and can mask permission/transient errors; no timeouts on DefaultClient; handlers stale if nodes change.

## Test Signals
No unit tests visible; deployment smoke test is ConfigMap creation plus HTTP proxy success for each node endpoint.
