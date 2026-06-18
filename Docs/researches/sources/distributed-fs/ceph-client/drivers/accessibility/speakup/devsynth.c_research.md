# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/devsynth.c Research

## Purpose
`devsynth.c` exposes Speakup speech injection devices to userspace through misc devices `/dev/synth` and `/dev/synthu`. The former accepts Latin-1 text and writes directly to the active synth; the latter accepts UTF-8, decodes it to `u16`, queues it in the synth buffer, and starts speech output.

## Important APIs And Control Flow
Public lifecycle functions are `speakup_register_devsynth()` and `speakup_unregister_devsynth()`. Open fails with `-ENODEV` if no synth exists and uses `xchg(&dev_opened, 1)` to enforce a single open across both devices. Latin-1 writes copy userspace data in 256-byte chunks, take `speakup_info.spinlock`, and call `synth_write()`. UTF-8 writes decode with `synth_utf8_get()`, skip invalid data, defer incomplete tails, then under the same spinlock call `synth_buffer_add()` and `synth_start()`. Reads return EOF.

## State And Persistence
Static flags track misc registration and one-open status: `synth_registered`, `synthu_registered`, and `dev_opened`. No user data persists after write completion. UTF-8 partial sequence progress is maintained only within a write call.

## Dependencies And Integration Points
This file depends on miscdevice registration, user copy helpers, Speakup globals, the synth write path, UTF-8 decoding, synth buffer, and the Speakup spinlock.

## Risks
One `dev_opened` flag serializes both devices. `dev_opened` is reset with a plain store on release after atomic open. Invalid UTF-8 is silently skipped. Large writes can return partial completion for incomplete UTF-8 tails. Holding the Speakup spinlock around synth operations requires those operations to be IRQ-safe and non-sleeping.

## Test Signals
Test misc registration and deregistration, single-open `-EBUSY`, no-synth `-ENODEV`, Latin-1 writes, UTF-8 valid/invalid/incomplete writes, partial returns, and module unload with devices registered.
