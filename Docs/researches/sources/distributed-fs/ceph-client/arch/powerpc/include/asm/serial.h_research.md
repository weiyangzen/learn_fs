<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h

Purpose: Provides PowerPC legacy serial-discovery declarations and default 8250 baud.

Important APIs/types/functions: `BASE_BAUD` and optional `find_legacy_serial_ports()`. Source-visible declarations include: #define _ASM_POWERPC_SERIAL_H; #define BASE_BAUD ( 1843200 / 16 ); extern void find_legacy_serial_ports(void);; #define find_legacy_serial_ports() do { } while (0).

Control flow: early platform setup calls the discovery hook when legacy serial support is built; other builds use a no-op macro. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serial port state is registered by platform code, not this header. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with 8250 discovery, early console, OF/platform serial setup.

Risks: legacy port probing can conflict with firmware-provided devices if discovery is enabled on the wrong platform. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h -->
