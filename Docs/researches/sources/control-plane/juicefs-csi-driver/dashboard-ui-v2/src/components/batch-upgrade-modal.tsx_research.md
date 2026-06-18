<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx

## Purpose
`batch-upgrade-modal.tsx` presents the UI for creating a batch mount-pod upgrade job from selected PVC/node criteria and a preview of pods with config diffs.

## Important APIs, Types, and Functions
`BatchUpgradeModal` uses `usePVCsWithUniqueId`, `usePVCsBasicInfo`, `useNodes`, and `useCreateUpgradeJob`. It manages selected PVC, resolved unique ID, selected node, worker count, ignore-error flag, generated job name, and `PodDiffConfig[]`. Helper functions are `getAllPVCs` and `genNewJobName`.

## Control Flow, State, and Persistence
Opening the modal renders inputs and a `PodToUpgradeTable`. Selecting a PVC updates `selectedPVCName`, which resolves `uniqueId`; node data fills the dropdown. The start button is disabled until diff pods exist. On start, it calls `actions.execute(worker, ignoreError, newJobName, selectedNode, uniqueId)`, closes the modal, and navigates to `/jobs/{jobName}`. `resetState` resets only some fields and does not regenerate the job name or clear ignore-error/diff state.

## Dependencies and Integration Points
It connects config-diff discovery, PVC lookup, node lookup, upgrade job creation, and router navigation. The `PodToUpgradeTable` child reports whether there is actionable work by calling `setDiffPods`.

## Risks and Test Signals
Risks include stale generated job names across repeated opens, partial reset behavior, no catch path for create-job failures, using `"All Nodes"` as both UI label and API value, and possible layout overflow in the wide `Space`. Signals are modal open/close state tests, PVC/node filtering tests, disabled start when no diffs exist, successful job creation navigation, and error-path rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx -->
