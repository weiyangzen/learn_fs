# sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.h

Purpose: private hardware definition header for the Nuvoton W83667HG/W83677HG-I consumer IR driver. It centralizes Super I/O IDs, CIR and CIR wake register offsets, FIFO encodings, sample-period constants, wake comparison sizing, and the runtime state structures consumed by `nuvoton-cir.c`.

Important APIs, types, and constants: `enum nvt_chip_ver` identifies supported chip IDs; `struct nvt_chip` maps names to versions; `struct nvt_dev` holds the `rc_dev`, spinlock, RX packet buffer, EFER register pair, CIR base/IRQ resources, chip revision fields, and carrier. Debug macros `nvt_dbg*` are controlled by the file-local `debug` variable. Key register groups include CIR data/control registers, CIR wake registers, Super I/O config registers, logical-device IDs, pinmux bits, MCE wake length thresholds, `SAMPLE_PERIOD`, `MIN_CARRIER`, `MAX_CARRIER`, and `WAKEUP_MAX_SIZE`.

Control flow: this header has no executable flow, but it defines the contract used by the driver when entering Super I/O extended function mode, selecting logical devices, enabling CIR/CIR wake resources, programming RX/TX FIFOs, interpreting hardware packet bytes, and comparing stored wake patterns.

State and persistence: all state is runtime and hardware-backed. `struct nvt_dev` stores volatile driver state and discovered hardware resources. CIR and wake registers persist only while the Super I/O device retains power/configuration. Wake comparison constants describe firmware/hardware wake pattern storage, not filesystem persistence.

Dependencies and integration points: depends on Linux spinlock/ioctl headers and `media/rc-core.h` constants via includers. It integrates the Nuvoton driver with rc-core raw event reporting, Super I/O logical-device configuration, ACPI/PME wake routing, and MCE-compatible wake pattern encoding.

Risks and edge cases: the header defines `static int debug`, so it is intended for one C translation unit; multiple inclusions into separate C files would create separate debug variables. Several timing and FIFO trigger choices are compile-time `FIXME` constants rather than runtime tunables. Floating-looking macro `CIR_SAMPLE_LOW_INACCURACY 0.85` is not an integer constant and must only be used in contexts that tolerate floating arithmetic. Wake matching uses tight fixed MCE length bands, so nonstandard remotes can fail wake programming.

Test signals: compile coverage of `nuvoton-cir.c`, probe on each supported chip ID, Super I/O resource discovery, RX/TX FIFO interrupt behavior, sample-period timing against logic-analyzer captures, carrier limits, and suspend/wake using the 65-byte wake comparison path.
