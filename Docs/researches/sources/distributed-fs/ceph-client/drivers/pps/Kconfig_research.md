# sources/distributed-fs/ceph-client/drivers/pps/Kconfig

Purpose: top-level Kconfig for LinuxPPS support.

Important entries: `menuconfig PPS` builds `pps_core.ko` and describes Pulse Per Second time-reference use cases. `PPS_DEBUG` enables debug messages by adding `-DDEBUG` in Makefiles. `NTP_PPS` enables the in-kernel hardpps consumer and depends on `!NO_HZ_COMMON`. It sources client and generator Kconfig files.

Control flow: selecting `PPS` opens subordinate options for clients and generators; `NTP_PPS` conditionally includes `kc.o` in the core build.

State/dependencies: configuration-only file; no runtime state. Depends on TTY/parport/platform-specific options indirectly through sourced Kconfigs.

Risks: `NTP_PPS` is unavailable with common tickless support, so kernel time synchronization may be absent even when PPS char devices are enabled.

Test signals: verify menu visibility, module names, `CONFIG_PPS_DEBUG` compile flags, and `CONFIG_NTP_PPS` gating of kernel consumer APIs.
