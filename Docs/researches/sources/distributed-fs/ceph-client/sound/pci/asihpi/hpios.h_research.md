# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.h

## Purpose
This header defines the Linux kernel OS abstraction layer used by AudioScience HPI code.

## Important APIs, Types, And Functions
Important definitions include `HPI_OS_LINUX_KERNEL`, `HPI_BUILD_KERNEL_MODE`, `struct consistent_dma_area`, inline DMA address/valid helpers, `struct hpi_ioctl_linux`, `HPI_IOCTL_LINUX`, debug-level printk mappings, `struct hpios_spinlock`, conditional lock helpers, and `struct hpi_adapter`.

## Control Flow
Inline lock flow chooses `spin_lock()` when IRQs are already disabled and `spin_lock_bh()` otherwise, storing the context for matching unlock. DMA getter helpers directly expose saved virtual and DMA addresses.

## State, Persistence, And Dependencies
State lives in caller-owned structures: DMA area metadata, spinlock context, and per-adapter PCI/ALSA/ioctl data. The header depends on Linux IO, ioctl, device, firmware, interrupt, PCI, mutex, and spinlock headers.

## Integration Points
It is included by HPI core, ioctl, and hardware-specific code to unify kernel APIs, locking, debug flags, and adapter state. `struct hpi_adapter` is the PCI drvdata shape used by `hpioctl.c`.

## Risks
`hpios_locked_mem_get_phys_addr()` truncates `dma_addr_t` into `u32`. `hpios_spinlock.lock_context` is shared per lock, so nested or cross-CPU misuse would unlock with the wrong primitive. The ioctl command uses a historically chosen command number that could conflict outside this driver.

## Test Signals
Build and runtime coverage should exercise HPI message paths from atomic and process contexts, coherent DMA address retrieval, ioctl ABI structure layout, and adapter mutex/buffer fields under concurrent user opens.
