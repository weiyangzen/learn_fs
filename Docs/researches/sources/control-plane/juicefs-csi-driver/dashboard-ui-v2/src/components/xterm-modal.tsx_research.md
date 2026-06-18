# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/xterm-modal.tsx

## Purpose
`XTermModal` provides an interactive terminal into a selected pod container.

## APIs, Control Flow, and State
It accepts namespace, pod name, container, and a render-prop trigger. Opening the modal connects to `/api/v1/ws/pod/:ns/:pod/:container/exec`. It creates an xterm instance, fits it on open and resize, writes incoming socket data to the terminal, sends `stdin` messages from user input, and sends `resize` messages with cols and rows.

## Dependencies and Integration Points
It depends on `xterm`, `xterm-react`, `@xterm/addon-fit`, Ant Design modal, and the shared `useWebsocket` heartbeat/base-path behavior. It is exposed from container action tables.

## Risks and Test Signals
The resize listener uses inline functions for add/remove, so removal will not unregister the original listener. `onOpen` may run before `terminal` state is set. Test open/close cycles, resizing, stdin delivery, backend close/error messages, and terminal disposal.
