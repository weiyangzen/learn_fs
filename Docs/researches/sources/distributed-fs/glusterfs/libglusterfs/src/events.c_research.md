# sources/distributed-fs/glusterfs/libglusterfs/src/events.c

## Purpose
This file sends GlusterFS event notifications as UDP datagrams to the configured event receiver. It formats event type, timestamp, and a caller-provided message into a compact string.

## Important APIs, types, and functions
The exported API is `_gf_event(eventtypes_t event, const char *fmt, ...)`. It uses `EVENT_PORT` 55555, default localhost behavior, `EVENT_LAST` validation, and event error/status constants such as `EVENT_SEND_OK`, `EVENT_ERROR_RESOLVE`, `EVENT_ERROR_SOCKET`, `EVENT_ERROR_MSG_FORMAT`, and `EVENT_ERROR_SEND`.

## Control flow
The function validates the event id, inspects `THIS->ctx->cmd_args` for `volfile_server` and `volfile_server_transport`, resolves either the volfile server or localhost with `getaddrinfo()`, creates the first usable datagram socket, formats the caller message with `gf_vasprintf()`, prefixes it with `gf_time()` and event id using `gf_asprintf()`, sends it with `sendto()`, then closes and frees resources.

## State and persistence behavior
There is no retained process state. Each event creates a socket, sends one datagram, and closes it. Delivery is best-effort UDP with no retry, acknowledgement, or persistence.

## Dependencies and integration points
The file depends on networking headers, `glusterfs/events.h`, `glusterfs/globals.h`, syscall wrappers, GlusterFS allocation helpers, and the active translator context through `THIS`. It integrates with CLI/daemon event consumers listening on the fixed event port.

## Risks and edge cases
The code assumes `THIS` and `THIS->ctx` are valid; early startup or non-translator contexts could crash. `getaddrinfo()` uses `AI_ADDRCONFIG`, which can surprise IPv4/IPv6-only environments. The host selection ignores unix volfile transport and otherwise targets the volfile server for clients. UDP send failures are reported only as status codes. Large formatted messages can exceed practical datagram size and be dropped or fragmented.

## Test signals
Tests should cover invalid event ids, localhost and volfile-server host selection, unix transport fallback, DNS failure, socket failure across addrinfo entries, format allocation failure, send failure, successful datagram contents with timestamp/event/message, and behavior with NULL or unavailable context where supported.
