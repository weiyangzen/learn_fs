<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.proto -->
# sources/cloud-native/containerd/api/types/transfer/progress.proto

Purpose: source schema for transfer progress telemetry.

Important APIs/types/functions: `Progress` fields are `event`, `name`, repeated `parents`, numeric `progress`/`total`, and a containerd descriptor.

Control flow: schema-only; semantics of event names and parent graph are external.

State/persistence: transient reporting state for long-running transfers.

Dependencies/integration: imports descriptor proto and is consumed by transfer clients.

Risks: weakly typed event/name strings can drift between producers and consumers. Numeric fields need clear handling for unknown totals.

Test signals: generated binding consistency and UI/client handling for event graphs and descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.proto -->
