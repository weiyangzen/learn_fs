## sources/distributed-fs/ceph-client/include/linux/mfd/cgbc.h

Purpose: This header defines the Congatec Board Controller MFD data structures and command helper API used by child drivers to exchange commands with the board controller.

Important APIs, types, and constants: `struct cgbc_version` stores feature, major, and minor revision bytes. `struct cgbc_device_data` stores mapped session and command I/O memory windows, the active session ID, parent device, version, and a mutex. `cgbc_command()` is the exported command transaction helper, taking command buffer/size, data buffer/size, and an optional returned status byte.

Control flow: Child drivers call `cgbc_command()`, which is expected to serialize command writes/reads using `cgbc_device_data.lock`, session state, and the two I/O windows. The exact command protocol is implemented elsewhere.

State and persistence: Runtime state includes the session ID and version. Hardware/firmware may maintain board-controller session state across calls; no filesystem persistence exists.

Dependencies and integration points: It relies on MMIO (`void __iomem`), `struct device`, `struct mutex`, and `u8` definitions from including contexts. It integrates with child drivers that expose board-controller features such as monitoring, GPIO, or platform controls.

Risks: The include guard is incomplete: the file has `#ifndef _LINUX_MFD_CGBC_H_` but no matching `#define _LINUX_MFD_CGBC_H_`, so multiple inclusion in one translation unit is not prevented. Command buffer sizes are caller supplied and need strict validation in implementation code.

Test signals: Build tests should catch duplicate inclusion or missing type includes depending on include order. Runtime tests should exercise serialized concurrent commands, command status propagation, session creation/recovery, and invalid size handling.
