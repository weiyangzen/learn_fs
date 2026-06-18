# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc.h

## Purpose
`efc.h` is the umbrella include for the libefc Fibre Channel discovery stack. It assembles common definitions, core object declarations, state-machine events, hardware command helpers, domain/nport/node/device/fabric/ELS APIs, and tracing macros.

## Important APIs, Types, And Functions
The header defines `EFC_MAX_REMOTE_NODES`, `NODE_SPARAMS_SIZE`, and SCSI deletion reason enums used when notifying the backend of initiator or target removal. `EFC_FC_ELS_DEFAULT_RETRIES` gives the default ELS retry budget. The trace macros `domain_sm_trace`, `domain_trace`, `node_sm_trace`, and `nport_sm_trace` standardize debug messages around current state handlers and `efc_sm_event_name`.

## Control Flow And State
There is no direct control flow, but this file shapes compilation and layering. Any `.c` file including `efc.h` sees the full discovery object graph and can post state-machine events, issue hardware commands, and send ELS messages. The tracing macros assume local variables named `evt`, `domain`, `node`, or `nport` exist in state handlers.

## Dependencies And Integration Points
`efc.h` includes `efc_common.h`, `efclib.h`, `efc_sm.h`, `efc_cmds.h`, and the state-machine-specific headers. This makes it the integration point between SLI-4 mailbox code, FC protocol helpers, Linux SCSI callbacks, and libefc object state machines.

## Risks And Test Signals
The main risk is include coupling: subtle changes to `efclib.h` or event enums propagate to all libefc implementation files. Trace macros also create compile-time coupling to variable names. Test signals are build coverage with all libefc objects, warning-free state handler compilation, and debug logging on domain/nport/node transitions.
