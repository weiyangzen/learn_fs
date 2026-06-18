# sources/distributed-fs/ceph-client/net/atm/signaling.h

## Purpose
`signaling.h` declares the internal ATM SVC signaling interface between SVC sockets, common ioctl code, and the signaling daemon bridge.

## Important APIs and State
- Exposes `extern struct atm_vcc *sigd` so SVC code can detect daemon availability.
- Declares `sigd_enq2`, the full request builder for signaling messages with VCC, listen VCC, PVC/SVC addresses, QoS, and reply fields.
- Declares `sigd_enq`, a convenience wrapper for common message shapes.
- Declares `sigd_attach`, used by privileged ioctl handling to bind the daemon socket.

## Control Flow and Integration
`svc.c` calls `sigd_enq*` before sleeping on VCC flags; `ioctl.c` calls `sigd_attach` for `ATMSIGD_CTRL`; `proc.c` includes the header to inspect signaling-related state. The header formalizes the daemon queueing contract but leaves all storage and synchronization to `signaling.c`.

## State and Persistence
No local state is stored in the header. It exposes the daemon singleton and the message-enqueue API that mutates live VCC/socket state.

## Risks and Test Signals
Risks are ABI drift between message construction and daemon reply handling, and direct external checks of `sigd` racing with daemon close. Test signals include builds of all SVC/signaling/proc users, daemon attach/detach behavior, and SVC operations returning `-EUNATCH` when `sigd` is absent.
