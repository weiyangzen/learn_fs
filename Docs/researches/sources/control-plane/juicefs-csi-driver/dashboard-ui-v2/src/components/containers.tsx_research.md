<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx

## Purpose
`containers.tsx` renders a pod's container status table and action buttons for logs, exec, access logs, debug collection, warmup, stats, and binary smooth upgrade.

## Important APIs, Types, and Functions
`Containers` accepts a `Pod` and optional `ContainerStatus[]`. It reads route params, version data, and utility predicates `isMountPod`, `isMountContainer`, `supportDebug`, and `supportBinarySmoothUpgrade`. It composes `LogModal`, `XTermModal`, `DebugModal`, `WarmupModal`, `StatsModal`, and `UpgradeModal`.

## Control Flow, State, and Persistence
The component is pure table rendering. For every container, basic log and terminal actions are always available. Mount pod/container conditions unlock access log, debug, warmup, stats, and upgrade actions. Upgrade is further gated by server-reported `disableGraceUpgrade` and image support.

## Dependencies and Integration Points
It integrates pod detail routes with websocket/download modals and smooth upgrade features. The actions depend on backend endpoints for logs, exec, debug, warmup, stats, and upgrade.

## Risks and Test Signals
Risks include using route params instead of pod metadata, invalid dates for non-running containers, record/c parameter confusion in render callbacks, and showing terminal/log actions for containers that backend may not permit. Signals are pod detail UI tests for mount and non-mount pods, image support gating, previous-log enablement, and action endpoint smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx -->
