# sources/distributed-fs/openafs/src/rx/rx_xmit_nt.h

## Purpose
Declares the Windows RX transmit shim and remaps POSIX-style `sendmsg`/`recvmsg` names to RX wrapper names.

## Important APIs, Types, And Functions
It declares `rxi_sendmsg`, `rxi_recvmsg`, and `rxi_xmit_init`, undefines `sendmsg`, defines `sendmsg` as `rxi_sendmsg`, and defines `recvmsg` as `rxi_recvmsg`.

## Control Flow
No runtime flow exists in the header. The macro remapping ensures code written against `sendmsg`/`recvmsg` calls the Windows-compatible shim.

## State And Persistence
The header stores no state; implementation state lives in `rx_xmit_nt.c`.

## Dependencies And Integration Points
It requires `osi_socket` and `struct msghdr` definitions from surrounding includes and is included by Windows RX packet/pthread code.

## Risks And Test Signals
Risks include declaration/name mismatches with implementation and macro remapping surprises in files that include other socket headers later. Windows compile/link coverage is the main signal.
