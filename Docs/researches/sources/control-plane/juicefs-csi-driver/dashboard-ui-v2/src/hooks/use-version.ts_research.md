# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-version.ts

## Purpose
`use-version.ts` exposes backend build/version data and the dashboard feature flag for graceful upgrade.

## APIs, Control Flow, and State
`VersionInfo` contains driverVersion, gitCommit, buildDate, goVersion, compiler, platform, and `disableGraceUpgrade`. `useVersion` fetches `/api/v1/version` with SWR, refreshes every five minutes, and disables focus revalidation.

## Dependencies and Integration Points
Batch upgrade list, config apply controls, pod/container action buttons, and smooth-upgrade gating use this hook.

## Risks and Test Signals
Feature controls depend on a timely version response; until loaded, some UI may appear enabled. Test disabled graceful-upgrade behavior, backend errors, and cache refresh.
