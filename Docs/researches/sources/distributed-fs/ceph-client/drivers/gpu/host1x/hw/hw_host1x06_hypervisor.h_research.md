<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h

## Purpose

`hw_host1x06_hypervisor.h` defines hypervisor-visible protection, gather-filter, and command FIFO peek registers for host1x06 (Tegra186). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT_PROT_EN, CH_KERNEL_FILTER_GBUFFER, optional CMDFIFO peek controls, ICG override, and HW8 MLOCK enable offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `dev.c`, `channel_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x06_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x06, probe on Tegra186, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h -->
