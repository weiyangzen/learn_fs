<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml -->
# sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml

Purpose: Helm values for deploying Longhorn's upgrade responder service with release metadata, telemetry schema, image settings, resources, and chart source metadata.

Important APIs/types/functions: top-level values include `applicationName`, `image`, `secret`, `resources`, `flags.scarfEndpoint`, `configMap.responseConfig`, `configMap.requestSchema`, `url`, `commit`, `releaseName`, and `namespace`. The embedded JSON defines stable/latest versions and request schemas for tags and numeric fields.

Control flow: the upgrade responder chart consumes these values to create application-specific database/configuration and answer version-check requests. `responseConfig` marks `v1.11.2` as latest/stable in this file, and `requestSchema` validates reported Longhorn environment, settings, counts, and resource metrics.

State and persistence: no runtime state in the file itself; deployed chart stores config in ConfigMaps/Secrets and writes collected check-in data to the configured InfluxDB database.

Dependencies/integration points: integrates with `longhornio/upgrade-responder:longhorn-head`, Scarf gateway endpoints, Helm, InfluxDB, and Longhorn manager's version-check payload shape.

Risks/test signals: schema drift can cause upgrade checks to reject new Longhorn fields or silently omit metrics. Version metadata can become stale. Test signals are Helm template validation, JSON parsing of embedded blocks, upgrade responder startup, `/v1/checkupgrade` responses, and ingest tests with representative Longhorn payloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/upgrade_responder_server/chart-values.yaml -->
