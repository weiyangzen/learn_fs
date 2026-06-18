<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/grafana.ini -->
# sources/cloud-native/buildkit/hack/composefiles/grafana.ini

Purpose: local Grafana security configuration for the development metrics profile.

Important APIs, types, and functions: under `[security]`, sets `admin_user = moby` and `admin_password = moby`.

Control flow and state: declarative config mounted into Grafana. The configured credentials affect the initial admin login.

Dependencies and integration: referenced by `compose.yaml` as `grafana_config` and mounted at `/etc/grafana/grafana.ini`.

Risks and test signals: hardcoded credentials are development-only. Test by starting the metrics profile and logging into Grafana with the configured values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/grafana.ini -->
