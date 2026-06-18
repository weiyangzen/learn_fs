<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h

## Purpose

`hw_host1x05_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x05 (Tegra210). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x05_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x05, probe on Tegra210, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h -->
