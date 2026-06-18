## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.h

Purpose: Publishes Gen2 hardware constants, register helpers, and helper prototypes.

Important APIs/types: Defines Gen2 RX/TX ring layout, AE-to-function mapping registers, admin mailbox offsets, arbiter offsets/config, power-gating fuse bits, default ring-to-service map, watchdog timer offsets/values, ECC/error-correction bits, heartbeat counter count, interrupt mask offsets, and prototypes for all Gen2 hardware helper functions.

Control flow/state: Macros directly address PMISC CSRs for IOV mapping and watchdog/error-control registers. No state is owned by the header.

Dependencies/integration: Included by Gen2 product drivers and common hardware-data code that installs function pointers and constants into `adf_hw_device_data`.

Risks and test signals: Offset or mask mistakes can break service routing, heartbeat, IOV mapping, or error correction. Tests should include boot/probe on Gen2 hardware, SR-IOV enable/disable, heartbeat operation, and compression/crypto instance creation using the default ring map.
