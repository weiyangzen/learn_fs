# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-detail.tsx

## Purpose
`ConfigDetail` is the main configuration editor for the CSI driver's dashboard ConfigMap.

## APIs, Control Flow, and State
It fetches config, matched PVCs, global config diff, and version data. It stores normalized YAML text, edit mode, active tab, update flag, diff flag, errors, and confirmation modal state. Effects parse `data.data['config.yaml']`, show YAML errors via notification, update diff state, and refresh config/diff when not locally updated. It renders Detail and YAML tabs, edit/reset/save controls, docs link, and Apply navigation to `/jobs?modalOpen=true` when config changes require mount pod upgrades and graceful upgrade is enabled.

## Dependencies and Integration Points
It composes `ConfigTablePage`, `ConfigYamlPage`, `ConfigUpdateConfirmModal`, config hooks, version hook, router navigation, and JuiceFS docs URL.

## Risks and Test Signals
The save disabled comparison stringifies strings rather than parsed objects. `updated` controls refresh suppression and must be reset carefully. Test missing ConfigMap, invalid YAML, tab switching, save confirmation, diff apply disabled states, and version-disabled upgrades.
