# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/main.tsx

## Purpose
`main.tsx` is the Vite React entry point for the dashboard UI.

## APIs, Control Flow, and State
It imports React, ReactDOM, `App`, and global CSS, then mounts `<App />` into `document.getElementById('root')!` under `React.StrictMode`. It has no persistence or custom state.

## Dependencies and Integration Points
The file depends on the HTML root element supplied by Vite and all top-level providers/routes configured in `App.tsx`.

## Risks and Test Signals
StrictMode can double-invoke effects in development, which matters for WebSocket hooks and fetch side effects during local testing. Test production build boot, root element existence, and dev mode modal/WebSocket behavior.
