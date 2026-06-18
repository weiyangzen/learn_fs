# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.h

## Purpose

`nitrox_mbx.h` is the small public header for Nitrox PF/VF mailbox support. It exposes initialization, cleanup, and interrupt-handler entry points used by SR-IOV setup and ISR code.

## Important APIs, Types, And Functions

- Include guard `__NITROX_MBX_H` prevents duplicate declarations.
- `int nitrox_mbox_init(struct nitrox_device *ndev)` allocates VF mailbox state and enables PF-to-VF mailbox interrupt handling.
- `void nitrox_mbox_cleanup(struct nitrox_device *ndev)` disables mailbox interrupts and releases mailbox workqueue/VF state.
- `void nitrox_pf2vf_mbox_handler(struct nitrox_device *ndev)` processes pending VF mailbox interrupt bits and queues responses.

## Control Flow

`nitrox_sriov_init()` calls `nitrox_mbox_init()` after registering SR-IOV interrupts. The ISR path calls `nitrox_pf2vf_mbox_handler()` when mailbox interrupts are signaled. SR-IOV cleanup and disable call `nitrox_mbox_cleanup()`.

## State And Persistence Behavior

The header declares functions that manipulate `ndev->iov` state but owns no state itself. Persistence is entirely in the Nitrox device object and mailbox hardware CSRs.

## Dependencies And Integration Points

The declarations require `struct nitrox_device` to be visible from including files such as `nitrox_sriov.c` and ISR code. This header is the boundary between SR-IOV lifecycle and mailbox implementation.

## Risks And Edge Cases

The header has no compile-time include of `nitrox_dev.h`, so include order must provide the forward type. API callers must obey lifecycle ordering: initialize after `iov.num_vfs`/queue mode are set and clean up before VF state is freed.

## Test Signals

Build coverage should catch declaration mismatches. Runtime signals are mailbox init/cleanup during SR-IOV enable/disable and ISR dispatch to `nitrox_pf2vf_mbox_handler()`.
