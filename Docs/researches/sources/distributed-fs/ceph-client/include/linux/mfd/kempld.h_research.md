# sources/distributed-fs/ceph-client/include/linux/mfd/kempld.h

Purpose: This header defines the Kontron PLD MFD register interface, device information structures, platform callbacks, and indexed I/O access helpers.

Important APIs, types, and functions: Constants define index/data I/O ports, mutex key, version/build/feature/spec registers, feature bits, IRQ/GPIO/I2C config, PLD clock, type values, and version string length. `struct kempld_info` stores parsed revision/build/type/spec/version data. `struct kempld_device_data` stores mapped I/O base/index/data, clock, feature mask, device, info, and mutex. `struct kempld_platform_data` supplies clock, GPIO base, I/O resource, hardware mutex callbacks, info callback, and cell registration callback. Exported helpers acquire/release the PLD mutex and read/write 8/16/32-bit indexed registers.

Control flow, state, and persistence: Parent code probes the indexed I/O region, parses version and feature registers, optionally uses hardware mutex callbacks, registers child cells, and serializes all indexed access. Persistent state includes PLD firmware version, feature bits, BIOS write-protect/config bits, watchdog/GPIO/I2C hardware state, and board-specific callbacks.

Dependencies and integration points: It integrates with MFD child registration for GPIO, I2C, watchdog, and possibly NMI/SMI/SCI signaling. It depends on resources, mutexes, MMIO/I/O access, and board platform data.

Risks and test signals: Risks include failing to serialize index/data accesses, wrong endian/width handling for 16/32-bit helpers, feature-mask misinterpretation, and platform callbacks not honoring hardware mutex semantics. Test signals include concurrent read/write stress, version parsing tests, feature-driven child registration, GPIO/I2C/watchdog child probes, and BIOS write-protect config readback.
