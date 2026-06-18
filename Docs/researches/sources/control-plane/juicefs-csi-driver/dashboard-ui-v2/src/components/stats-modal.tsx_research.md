# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/stats-modal.tsx

## Purpose
`StatsModal` streams real-time JuiceFS mount statistics for a selected container and lets users choose schema sections.

## APIs, Control Flow, and State
The memoized component accepts namespace, pod name, `ContainerStatus`, and a render-prop trigger. It derives CE/EE behavior from `isEEImage`, tracks modal/open/start state, Monaco editor instance, auto-scroll, and schema checkboxes. `getSchema()` builds the query string for `/api/v1/ws/pod/:ns/:pod/:container/stats`. WebSocket messages are ANSI-stripped via `createAnsiStrippedMessageHandlerWithCallback`, appended to editor data, and used to decide whether auto-reveal should continue.

## Dependencies and Integration Points
It integrates with `Containers`, `useWebsocket`, Monaco, Ant Design modal controls, `isEEImage`, and the backend stats WebSocket protocol.

## Risks and Test Signals
Long streams accumulate entirely in React state. Auto-scroll depends on Monaco visible range timing. Schema defaults differ for CE and EE. Test CE/EE image tags, start/refresh/close behavior, WebSocket close, ANSI output, and manual scrolling.
