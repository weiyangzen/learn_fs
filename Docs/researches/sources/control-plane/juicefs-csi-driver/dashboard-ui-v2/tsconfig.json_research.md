# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.json

## Purpose
This TypeScript config defines the browser app compilation contract for the Vite React dashboard.

## APIs, Control Flow, and State
It targets ES2020 with DOM libs, ESNext modules, bundler resolution, JSON modules, isolated modules, no emit, React JSX transform, strict checks, unused checks, fallthrough checks, and `@/*` alias to `./src/*`. It includes `src`, excludes `node_modules`, and references `tsconfig.node.json`.

## Dependencies and Integration Points
Vite, editor tooling, and type checking depend on this config. The alias must match `vite.config.ts`.

## Risks and Test Signals
`allowImportingTsExtensions` supports existing `.ts`/`.tsx` import suffixes but may affect portability. Test `tsc -b`, Vite build, path alias resolution, and strict unused parameter/local failures.
