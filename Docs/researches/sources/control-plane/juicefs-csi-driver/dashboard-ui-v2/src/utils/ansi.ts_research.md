# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/ansi.ts

## Purpose
This utility strips ANSI terminal sequences from streamed WebSocket output and provides a reusable React state append handler.

## APIs, Control Flow, and State
`removeAnsiSequences(text)` applies a control-sequence regex. `createAnsiStrippedMessageHandlerWithCallback(setData, callback)` returns an `onMessage` handler that strips `msg.data`, appends it to a React string state, and invokes an optional callback with the cleaned data.

## Dependencies and Integration Points
`StatsModal` uses this shared handler. Similar logic exists locally in `WarmupModal`, which could be consolidated.

## Risks and Test Signals
The regex covers common CSI-style ANSI escape sequences but not every terminal control form. Test colored output, cursor control, plain text, binary/unicode output, and callback invocation order.
