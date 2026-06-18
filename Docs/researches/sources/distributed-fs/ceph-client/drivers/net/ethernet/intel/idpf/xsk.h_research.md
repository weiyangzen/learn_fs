# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.h

## Purpose
Declares the IDPF AF_XDP integration surface used by the rest of the IDPF driver. The header keeps implementation details in `xsk.c` while exposing queue setup, teardown, polling, transmit, pool setup, and wakeup functions.

## Important APIs, Types, And Functions
The file forward-declares IDPF queue/vport types, `struct net_device`, and `struct netdev_bpf`, and includes `<linux/types.h>` for scalar types. Public prototypes cover `idpf_xsk_setup_queue`, `idpf_xsk_clear_queue`, `idpf_xsk_init_wakeup`, `idpf_xskfq_init`, `idpf_xskfq_rel`, `idpf_xsksq_clean`, `idpf_xskrq_poll`, `idpf_xsk_xmit`, `idpf_xsk_pool_setup`, and `idpf_xsk_wakeup`.

## Control Flow
This header has no executable control flow. It defines how other IDPF modules call into XSK handling: setup/clear during queue lifecycle, fill-queue init/release during buffer queue lifecycle, RX polling from NAPI, TX from wakeup/timer paths, and pool setup from netdev BPF callbacks.

## State And Persistence
No state is stored in the header. The prototypes imply mutation of queue objects, XSK pool references, queue wakeup state, and netdev BPF pool registration in implementation code.

## Dependencies And Integration
Depends on Virtchnl2 queue type declarations and IDPF internal structs. It is the integration point between generic IDPF queue management, XDP, AF_XDP, and netdev operations.

## Risks
Signature drift here can silently break callers across IDPF queue, XDP, and netdev code. The `void *q` queue setup/clear API requires callers to pass an object matching the supplied queue type.

## Test Signals
Build coverage with `CONFIG_IDPF` and AF_XDP enabled, plus queue lifecycle tests that exercise every declared entry point through normal driver paths.
