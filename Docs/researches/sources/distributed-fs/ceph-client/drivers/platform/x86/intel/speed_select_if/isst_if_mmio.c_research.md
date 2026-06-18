# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mmio.c

## Purpose

This backend exposes selected Speed Select P-unit MMIO registers through the common ioctl interface for RAPL priority devices.

## Important APIs, Types, And Functions

`struct isst_if_device` stores the mapped P-unit MMIO base, valid register ranges, suspend snapshots, and a mutex. `isst_if_mmio_rd_wr()` validates register alignment and range, enforces CAP_SYS_ADMIN for writes, finds the PCI device for the target CPU, and performs serialized `readl()` or `writel()`. Probe computes the base address from PCI config registers `0xD0` and `0xFC`, maps the selected range, and registers the MMIO callback. PM ops save and restore configured ranges.

## Control Flow

The PCI driver matches RAPL priority device IDs with different range tables. Runtime ioctls dispatch through the common `ISST_IF_IO_CMD` path. Suspend snapshots both allowed ranges; resume writes them back.

## State And Persistence

State is per PCI device and includes cached register snapshots used for suspend/resume restoration. User writes are hardware state and may be restored after system sleep.

## Dependencies And Integration Points

The file depends on PCI config access, ioremap resource handling, common ISST CPU-to-PCI mapping, and common char-device callbacks.

## Risks

Range validation checks only the overall first-begin to second-end interval, not holes between ranges, so an address in the gap could pass if hardware exposes one. Base address calculation is device-specific and sensitive to config format. Multiple devices share one common MMIO callback slot.

## Test Signals

Probe on both device IDs, mapping address correctness, aligned read/write ioctls, rejection of unaligned/out-of-range writes, privilege enforcement, and suspend/resume state restoration are key signals.
