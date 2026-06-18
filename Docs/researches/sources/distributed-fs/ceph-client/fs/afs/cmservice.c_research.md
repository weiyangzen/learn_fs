# sources/distributed-fs/ceph-client/fs/afs/cmservice.c

## Purpose
`cmservice.c` implements the incoming AFS/YFS cache-manager RxRPC service. It dispatches callback/probe/capability operations, unmarshals request payloads, schedules work handlers, breaks callbacks before replying, and sends replies or aborts.

## Important APIs, types, and functions
The public dispatcher is `afs_cm_incoming_call()`. Important call types are `afs_SRXCBCallBack`, `afs_SRXCBInitCallBackState`, `afs_SRXCBInitCallBackState3`, `afs_SRXCBProbe`, `afs_SRXCBProbeUuid`, `afs_SRXCBTellMeAboutYourself`, and `afs_SRXYFSCB_CallBack`. Delivery/work handlers include `afs_deliver_cb_callback()`, `SRXAFSCB_CallBack()`, `afs_deliver_cb_init_call_back_state*()`, `SRXAFSCB_InitCallBackState()`, `afs_deliver_cb_probe*()`, `SRXAFSCB_Probe*()`, `afs_deliver_cb_tell_me_about_yourself()`, `SRXAFSCB_TellMeAboutYourself()`, and `afs_deliver_yfs_cb_callback()`.

## Control flow
Incoming calls are matched by operation ID and service. Deliver functions incrementally extract XDR data across network fragments, validate counts, allocate request buffers, and transition to server reply state. Work handlers perform actions: break callbacks before replying, reset callback state, answer probes, compare UUIDs for ProbeUuid, and return interface/capability data for TellMeAboutYourself.

## State and persistence
Per-call runtime state includes unmarshalling stage, temporary buffer, callback count arrays, UUID request buffers, server/net references, and reply state. It mutates callback cache state through `callback.c` but stores no durable data.

## Dependencies and integration points
It depends on RxRPC call helpers, AFS/YFS protocol constants, callback invalidation, net UUIDs, server UUIDs, tracing, workqueues, and abort/error translation.

## Risks and test signals
Risks include XDR count validation, partial receive state bugs, memory leaks in call buffers, callback reply ordering, UUID endian conversion, unsupported YFS service dispatch, and abort semantics. Test signals include CB.CallBack with zero/max/over-limit counts, mismatched callback counts, InitCallBackState3 UUID mismatch, ProbeUuid positive/negative, capability reply decoding, YFS 64-bit fid callbacks, and fragmented RxRPC delivery.
