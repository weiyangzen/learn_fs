# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.node.json

## Purpose
This TypeScript config covers Node-side tooling code, currently Vite configuration.

## APIs, Control Flow, and State
It enables composite project output metadata, skips library checks, uses ESNext modules with bundler resolution, allows synthetic default imports, enables strict mode, and includes only `vite.config.ts`.

## Dependencies and Integration Points
It is referenced from the main tsconfig and supports `tsc -b` checking of Vite config.

## Risks and Test Signals
Because the include set is narrow, any additional Node scripts need explicit inclusion or another config. Test project references and Vite config type checking.
