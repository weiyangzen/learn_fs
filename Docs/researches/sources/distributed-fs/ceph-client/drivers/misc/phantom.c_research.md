# sources/distributed-fs/ceph-client/drivers/misc/phantom.c

Purpose: PCI character driver for Sensable Phantom haptic devices behind a PLX 9050 bridge, exposing ioctl-driven register access, polling for device interrupts, and a class version attribute.

Important APIs and types: `struct phantom_device` stores mapped control/input/output BAR addresses, status flags, interrupt counter, waitqueue, cdev, open lock, register spinlock, and NOT_OH mode shadow registers. File operations are `phantom_open()`, `phantom_release()`, `phantom_ioctl()`, compat ioctl, and `phantom_poll()`. PCI lifecycle is `phantom_probe()`, `phantom_remove()`, suspend/resume, module init/exit.

Control flow: module init registers class, version file, char-device range, and PCI driver. Probe enables PCI, reserves a minor, requests regions, maps BAR0/BAR2/BAR3, disables IRQs, requests shared IRQ, adds a cdev, and creates `/dev/phantomN`. Ioctls read/write individual or multiple registers, enforce register index <= 7, start/stop IRQ mode via `phantom_status()`, preserve amplifier state in NOT_OH mode, and copy data to/from userspace. ISR checks control IRQ enable, acknowledges device registers, optionally replays shadow output regs/toggles amp in NOT_OH mode, increments a counter, and wakes poll waiters.

State and persistence: per-device kernel state includes minor allocation, open count, status flags, shadow regs, and interrupt counter. Hardware register writes affect device state until reset.

Dependencies and integration points: depends on `linux/phantom.h` UAPI, PCI PLX IDs, char devices, class devices, poll, compat ioctl handling, and shared IRQ semantics.

Risks and test signals: only one opener is allowed; races around open/remove need attention. The driver performs direct hardware register writes from userspace-provided values. ISR and ioctl share register state via spinlock, while open state uses mutexes. Tests should cover exclusive open, ioctl validation and compat sizes, poll behavior with IRQs disabled/enabled, NOT_OH mode before/after running, suspend/resume IRQ masking, probe error unwind, and multi-device minor exhaustion.
