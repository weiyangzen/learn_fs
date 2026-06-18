<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx

## Purpose
`log-modal.tsx` streams pod container logs or mount access logs into a Monaco editor and supports full log download and current/previous log switching.

## Important APIs, Types, and Functions
`LogModal` is memoized and accepts namespace, pod name, container, previous-log capability, log type, and render-prop children. It uses `useWebsocket`, `useDownloadPodLogs`, Monaco editor refs, and Ant Design modal buttons.

## Control Flow, State, and Persistence
Opening the modal connects to `/api/v1/ws/pod/{namespace}/{name}/{container}/{type}` with `previous` as a query parameter. Incoming data appends to local text and auto-scrolls only if the user was already at the bottom. Closing clears log data. Previous/current toggling clears the buffer and changes websocket query params. Download is available only for normal logs.

## Dependencies and Integration Points
It is used by container action tables and depends on backend websocket/download APIs. Monaco worker setup is global in `App.tsx`.

## Risks and Test Signals
Risks include unlimited log buffer growth, no websocket error state, stale auto-scroll decisions if editor ranges are absent, a console log left in production, and no download type parameter for access logs. Signals are websocket append tests, previous-log switching, auto-scroll behavior, close/reset behavior, and large-log performance checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx -->
