<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts

## Purpose
`index.ts` is the barrel export for commonly used dashboard components.

## Important APIs, Types, and Functions
It imports and re-exports `Containers`, `DebugModal`, `EventTable`, `Layout`, `PodBasic`, `PodsTable`, `PVBasic`, `PVCBasic`, `ResourceDetail`, `ResourceList`, and `YamlModal`.

## Control Flow, State, and Persistence
There is no runtime control flow beyond module evaluation. It centralizes import paths for consumers such as `App.tsx`.

## Dependencies and Integration Points
The file creates a stable public surface for the components folder. Components not listed here must be imported directly, which separates generic/detail components from specialized modals/tables.

## Risks and Test Signals
Risks include circular dependencies because `containers.tsx` imports `DebugModal` from `.`, stale exports after component renames, and inconsistent import style across the app. Signals are TypeScript build success and dependency-cycle checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts -->
