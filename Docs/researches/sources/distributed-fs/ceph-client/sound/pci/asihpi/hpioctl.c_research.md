# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.c

## Purpose
This file implements the Linux userspace ioctl boundary for HPI messages plus PCI probe/remove and module init/exit support for AudioScience adapters.

## Important APIs, Types, And Functions
Key APIs are `asihpi_hpi_ioctl()`, `asihpi_hpi_release()`, `hpi_send_recv()`, `asihpi_adapter_probe()`, `asihpi_adapter_remove()`, `asihpi_init()`, and `asihpi_exit()`. The static `adapters[]` array stores per-adapter kernel state, stream bounce buffers, mutexes, IRQ callbacks, and HPI adapter pointers.

## Control Flow
The ioctl handler validates `HPI_IOCTL_LINUX`, allocates kernel message/response buffers, copies user pointers and message data, clamps message and response sizes, blocks userspace create/delete adapter operations, and dispatches subsystem or adapter messages. Stream read/write requests extract embedded user data pointers, resize a per-adapter vmalloc buffer under the adapter mutex, copy data in for playback, send the message, then copy data out for capture. Probe enables PCI, maps BAR memory, creates the HPI adapter, opens it, checks low-latency and IRQ support, registers optional threaded IRQs, and records driver data. Remove disables IRQ generation, deletes the adapter, unmaps memory, frees IRQ and buffers, and clears state.

## State, Persistence, And Dependencies
State persists in `adapters[]`, module parameters `prealloc_stream_buf` and `hpi_debug_level`, PCI drvdata, vmalloc stream buffers, and IRQ callback fields. Dependencies include Linux PCI, uaccess, vmalloc, module firmware declarations, HPI init/router/common code, and `hpios.h` structures.

## Integration Points
This is both the character-device ioctl implementation and the PCI lifecycle bridge into `hpimsgx.c`. `hpi_send_recv()` is exported for in-kernel HPI callers using `HOWNER_KERNEL`.

## Risks
The ioctl path handles user-controlled sizes and embedded pointers, making bounds and copy handling critical. Partial stream-buffer copies are logged but do not necessarily fail the ioctl. Probe error unwinding only unmaps BARs through the current index loop, and adapter deletion is skipped on some early failure paths after create. Shared per-adapter bounce buffers serialize ioctl stream traffic and may be large.

## Test Signals
Signals include invalid command rejection, small response-size rejection, userspace create/delete denial, stream read/write copy fault behavior, PCI probe/remove with and without IRQ support, low-latency IRQ callbacks, firmware load paths, and clean subsystem close on file release.
