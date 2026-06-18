# sources/distributed-fs/ceph-client/include/net/tls_prot.h

## Purpose

`tls_prot.h` provides TLS protocol number definitions used by kernel TLS and related parsers. It mirrors IANA TLS content type, alert level, and alert description values in a kernel header.

## Important APIs, types, and functions

The header defines anonymous enums for record content types (`TLS_RECORD_TYPE_*`), alert levels (`TLS_ALERT_LEVEL_WARNING`, `TLS_ALERT_LEVEL_FATAL`), and alert descriptions such as `TLS_ALERT_DESC_CLOSE_NOTIFY`, `BAD_RECORD_MAC`, `RECORD_OVERFLOW`, `HANDSHAKE_FAILURE`, `PROTOCOL_VERSION`, `INTERNAL_ERROR`, and `NO_APPLICATION_PROTOCOL`.

## Control flow

There is no executable control flow. Consumers compare parsed TLS record or alert bytes against these symbolic constants when classifying TLS data or generating alerts.

## State and persistence behavior

The header owns no state. Numeric values are wire protocol ABI and must remain stable.

## Dependencies and integration points

It has no local includes. It integrates with kTLS record handling, TLS offload code, protocol parsers, and any code that needs TLS alert/content names without pulling in larger TLS internals.

## Risks and test signals

Risks include numeric mismatch with IANA assignments, missing alert values needed by parsers, and treating TLS constants as kernel-private. Tests should verify parsed record content types and alert descriptions against known TLS frames and compile users without broader TLS headers.
