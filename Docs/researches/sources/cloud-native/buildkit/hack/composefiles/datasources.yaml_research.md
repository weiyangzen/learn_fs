<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/datasources.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/datasources.yaml

Purpose: Grafana provisioning file that registers Prometheus as the default datasource for the local development metrics stack.

Important APIs, types, and functions: `apiVersion: 1`, datasource named `Prometheus`, type `prometheus`, proxy access, URL `http://prometheus:9090`, default flag, POST method, alert management disabled, Prometheus version `2.48.1`, no cache, recording rules enabled, 10 minute overlap, and empty exemplar trace destinations.

Control flow and state: declarative provisioning consumed by Grafana at startup. State is stored by Grafana in its volume after provisioning.

Dependencies and integration: mounted by `compose.yaml` into Grafana provisioning. It assumes the Compose service name `prometheus` and matching Prometheus version.

Risks and test signals: cache disabled is appropriate for development but inefficient elsewhere. Version drift with the Prometheus image should be kept aligned. Test by starting the metrics profile and checking Grafana datasource health.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/datasources.yaml -->
