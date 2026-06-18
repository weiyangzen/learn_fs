<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml -->
# sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml

Purpose: minimal chart metadata pointer for the Longhorn upgrade responder deployment.

Important APIs/types/functions: declares chart `url` as the upgrade responder GitHub repository, a pinned `commit`, `releaseName: longhorn-upgrade-responder`, and `namespace: longhorn-upgrade-responder`.

Control flow: automation can use this file to locate the chart source and deploy a known revision under the specified release/namespace.

State and persistence: no runtime state; it is deployment metadata.

Dependencies/integration points: depends on the upgrade responder repository and the pinned commit being fetchable. It complements `chart-values.yaml`.

Risks/test signals: stale commits or moved repositories break reproducible deployment. Test signals are repository fetch, commit checkout, Helm chart discovery, and consistency with the values file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart.yaml -->
