# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/warmup-modal.tsx

## Purpose
`WarmupModal` starts and streams JuiceFS cache warmup for a mount container.

## APIs, Control Flow, and State
The memoized component tracks modal/open/start state plus warmup parameters: threads, IO retries, max failure, background, check, and subPath. It chooses CE or EE help text from `isEEImage`; EE exposes retries and max-failure controls. Start connects to `/api/v1/ws/pod/:ns/:pod/:container/warmup` with query parameters and appends ANSI-stripped output to a read-only Monaco editor.

## Dependencies and Integration Points
It is launched from container actions and depends on `useWebsocket`, Ant Design form controls, Monaco, Kubernetes `ContainerStatus`, and the backend warmup WebSocket endpoint.

## Risks and Test Signals
The component has a local ANSI stripper duplicated with `utils/ansi.ts`. `InputNumber` changes ignore `0` because of truthy checks. Long output is unbounded. Test CE/EE images, zero/negative numeric values, query serialization, close/reopen reset, and backend close.
