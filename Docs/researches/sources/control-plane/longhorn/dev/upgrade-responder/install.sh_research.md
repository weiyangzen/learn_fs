<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/install.sh -->
# sources/control-plane/longhorn/dev/upgrade-responder/install.sh

Purpose: end-to-end development installer for InfluxDB, Longhorn upgrade responder, and Grafana in a Kubernetes cluster.

Important APIs/types/functions: constants define repository, branch, generated values file, image, InfluxDB URL, app name, and timeouts. Functions `wait_for_deployment`, `install_influxdb`, `install_grafana`, `install_upgrade_responder`, and `output` orchestrate `kubectl`, `git clone`, `helm upgrade --install`, and status reporting.

Control flow: copies the current directory to a temporary directory, applies InfluxDB manifests and waits, writes a Helm values file with secrets/schema/release response/image, clones the upgrade responder repo, installs the chart, waits, installs Grafana, then prints service URLs and credentials, including a public IP fetched from `ifconfig.me`.

State and persistence: creates Kubernetes Secrets, PVCs, Deployments, Services, and a Helm release. Temporary files are removed on exit; generated values exist only in the temp directory.

Dependencies/integration points: depends on `kubectl`, `helm`, `git`, outbound network access, Longhorn StorageClass, InfluxDB, Grafana, Scarf URLs, and the upgrade responder chart.

Risks/test signals: embeds root/root and admin/admin demo credentials, uses external public IP lookup, and waits on `kubectl rollout status` without namespace flags. Test signals are Helm render/install success, deployment rollout, service reachability, InfluxDB database creation, and successful upgrade-check request ingestion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/install.sh -->
