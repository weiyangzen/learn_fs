<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/prometheus.yml -->
# sources/cloud-native/buildkit/hack/composefiles/prometheus.yml

Purpose: Prometheus scrape config for local BuildKit debug metrics.

Important APIs, types, and functions: defines one scrape job `buildkit`, scrape interval `1m`, target `buildkit:6060`.

Control flow and state: declarative scrape configuration. Prometheus stores scraped time series in its named volume.

Dependencies and integration: assumes BuildKit debug address is enabled on port 6060 by `buildkitd.toml` and service DNS name `buildkit` exists in Compose.

Risks and test signals: if debug address or service name changes, scraping silently fails except Prometheus target health. Test in Prometheus UI and Grafana datasource queries.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/prometheus.yml -->
