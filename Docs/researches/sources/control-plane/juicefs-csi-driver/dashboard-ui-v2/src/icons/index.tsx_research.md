# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/icons/index.tsx

## Purpose
This module centralizes custom dashboard icons for resource navigation and actions.

## APIs, Control Flow, and State
It imports Ant Design `Icon`, image assets for common Kubernetes resources, and defines React wrapper components such as `DSIcon`, `PODIcon`, `PVIcon`, `PVCIcon`, `SCIcon`, `CMIcon`, and `LOGOIcon`. It also defines inline SVG icons for locale, terminal, logs, access logs, YAML, debug, warmup, stats, upgrade, gather, resources, diff, delete, pause, resume, and stop. All are exported as named components accepting partial Ant Design icon props.

## Dependencies and Integration Points
Components throughout the dashboard import these icons for buttons, menus, and toolbars. The path alias `@/assets/*` depends on Vite/tsconfig aliasing.

## Risks and Test Signals
Inline SVGs are large and untyped beyond icon props; image icons use `width` but not alt text. Test asset bundling, tree-shaking, button rendering at different sizes, and missing asset paths.
