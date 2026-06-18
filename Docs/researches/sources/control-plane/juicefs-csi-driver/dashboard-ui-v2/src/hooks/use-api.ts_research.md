# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-api.ts

## Purpose
This file provides general pod, node, WebSocket, and download hooks for the dashboard.

## APIs, Control Flow, and State
`useAppPods` and `useSysAppPods` build paginated/sorted pod list SWR URLs. Detail and relationship hooks fetch pod, event, mount pod, CSI node, PV, PVC, and node data. `useWebsocket` wraps `react-use-websocket`, computes `ws`/`wss`, uses `VITE_HOST` or current host plus `getBasePath`, adds a ping heartbeat, filters `pong`, and forwards other messages. Download hooks fetch blobs and create temporary anchor downloads for logs/debug ZIPs.

## Dependencies and Integration Points
Nearly all pod pages and modals use this layer. It depends on `apiFetchBlob`, `getBasePath`, Kubernetes types, SWR, `useAsync`, and `react-use-websocket`.

## Risks and Test Signals
WebSocket URLs are built even when `uri` is undefined, relying on `shouldConnect`. Downloads create browser object URLs. Test hosted subpath deployments, HTTPS, VITE_HOST override, heartbeat handling, blob errors, and SWR keys with optional params.
