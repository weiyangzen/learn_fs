# sources/distributed-fs/ceph-client/drivers/char/sonypi.c

## Purpose
`sonypi.c` is the legacy Sony VAIO Programmable I/O controller driver. It detects supported VAIO systems, configures model-specific I/O ports and IRQs, translates hardware events to a misc-device event stream and optional input devices, and provides ioctls for brightness, battery, Bluetooth, fan, and temperature controls.

## Important APIs, Types, and Functions
- Module parameters control minor selection, verbosity, Fn-key initialization, MotionEye camera support, compatibility mode, event mask, input integration, and I/O-port conflict checking.
- Event decoding is table-driven with `struct sonypi_event`, `sonypi_eventtypes[]`, and `sonypi_inputkeys[]`.
- Global `sonypi_device` holds PCI device, IRQ, I/O ports, model, camera/Bluetooth state, locks, event FIFO, input FIFO, wait queue, fasync state, and input device pointers.
- EC helpers `sonypi_ec_read()`/`sonypi_ec_write()` use ACPI EC when active or raw ports `0x62/0x66`.
- Model setup/disable functions `sonypi_type1_srs()`, `sonypi_type2_srs()`, `sonypi_type3_srs()` and matching `_dis()` functions program PCI/EC registers.
- `sonypi_irq()` reads event bytes, matches enabled event tables, reports input events, queues misc events, sends fasync, and wakes readers.
- `sonypi_misc_read()`, `sonypi_misc_poll()`, `sonypi_misc_fasync()`, and `sonypi_misc_ioctl()` implement the user ABI.
- `sonypi_probe()` performs DMI/platform setup, PCI model detection, I/O region and IRQ selection, misc registration, optional input registration, and hardware enable.

## Control Flow
Module init first checks DMI for Sony VAIO product patterns, registers a platform driver/device, and optionally registers an ACPI companion driver. Probe allocates the misc FIFO, detects model type by Intel bridge IDs, selects I/O/IRQ tables, reserves one available I/O pair, requests a shared IRQ, registers the misc device, creates input devices if requested, allocates the input FIFO, initializes work, and enables hardware event delivery. Interrupts decode events into the FIFO and input subsystem. Suspend disables hardware while preserving camera power; resume re-enables it.

## State and Persistence
Most state is global and volatile. Hardware state includes EC registers, Bluetooth power, camera power, PCI routing, and event enablement. The misc FIFO is reset on first open, but input events are independent. Camera/Bluetooth state is cached in `sonypi_device` and restored across suspend for camera.

## Dependencies and Integration Points
The driver integrates with DMI, PCI, ACPI EC/platform matching, raw I/O ports, IRQ handling, misc core, Linux input subsystem, kfifo, fasync, wait queues, workqueues, and platform PM. It warns users to prefer `sony-laptop`, indicating legacy overlap.

## Risks
- Raw EC and I/O-port access is model-specific and can conflict with `sony-laptop`; the conflict check is explicitly racy.
- Global state assumes one device instance.
- IRQ handler queues events without backpressure beyond kfifo capacity semantics; event loss is possible if FIFO fills.
- Some hardware command waits only warn on timeout and continue.
- User ioctls can modify platform controls such as brightness, fan, and Bluetooth without extra policy checks.

## Test Signals
Testing should cover DMI rejection, model detection, I/O-port conflict failure, IRQ table fallback, misc FIFO blocking/nonblocking reads, fasync and poll, input event generation and delayed key release work, ioctl EC read/write behavior, suspend/resume camera restoration, and cleanup ordering with IRQ synchronization and work flush.
