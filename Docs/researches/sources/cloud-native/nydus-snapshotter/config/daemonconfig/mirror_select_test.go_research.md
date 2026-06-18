# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirror_select_test.go

Purpose: tests mirror URL splitting and live mirror selection fallback.

Flow: table tests validate schemes/hosts for http, https, no scheme, ports, and paths. Selection tests cover no config, empty dir, mirror without ping URL, successful ping, failed ping fallback to origin, and first-fail second-no-ping selection.

State/dependencies: creates temp `hosts.toml` directories and httptest servers.

Integration points: protects registry mirror choice used during daemon config supplementation.

Risks/signals: no CA cert assertions here; no timeout behavior test. Invalid URL expect-error cases are not populated in the table.
