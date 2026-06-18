# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/vite.config.ts

## Purpose
This file configures Vite for the React dashboard development server and production build.

## APIs, Control Flow, and State
`defineConfig` enables the React plugin, relative `base: './'`, `@` alias to `src`, dev-server proxies for `/api` HTTP and `/api/v1/ws` WebSocket traffic to localhost:8088, and a production build target list. Build output config uses `rolldownOptions.output.codeSplitting.groups` to group `antd` and `@ant-design` dependencies.

## Dependencies and Integration Points
It must align with tsconfig paths, dashboard backend port, static hosting under the CSI dashboard image, and Vite/Rolldown version support.

## Risks and Test Signals
`rolldownOptions` is version-sensitive; older Vite versions may not accept it. Relative base supports embedded static serving but can affect router refreshes. Test `npm run dev`, WebSocket proxying, production build, and serving assets from subpaths.
