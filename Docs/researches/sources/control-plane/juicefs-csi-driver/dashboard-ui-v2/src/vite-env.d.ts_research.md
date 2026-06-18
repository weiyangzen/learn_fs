# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/vite-env.d.ts

## Purpose
This declaration file extends Vite client typings with dashboard-specific environment variables.

## APIs, Control Flow, and State
It references `vite/client` and declares `ImportMetaEnv.VITE_HOST` as a readonly string, plus `ImportMeta.env`. There is no runtime output.

## Dependencies and Integration Points
`getHost` and `useWebsocket` read `import.meta.env.VITE_HOST` to override the API/WebSocket host.

## Risks and Test Signals
`VITE_HOST` is typed as always present even though runtime code treats it as optional. Test TypeScript compilation and builds with and without the variable.
