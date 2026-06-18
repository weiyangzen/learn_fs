<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig

Purpose: this Kconfig file defines build options for Bosch CC770 and Intel AN82527 CAN controller support and its ISA and platform bus front ends.

Important APIs, types, and functions: `CAN_CC770` is the parent tristate and depends on `HAS_IOMEM`. `CAN_CC770_ISA` enables legacy ISA support and depends on `HAS_IOPORT`. `CAN_CC770_PLATFORM` enables directly attached platform bus support.

Control flow: selecting `CAN_CC770` exposes the ISA and platform wrappers. The core `cc770.o` is built for the parent, while each wrapper is compiled only when its symbol is enabled.

State and persistence: this is build-time configuration only; it decides which CC770 objects are available.

Dependencies and integration points: it integrates with the top-level CAN Kconfig and Makefile. ISA support requires port IO capability, while platform support relies on memory-mapped device resources handled by the corresponding wrapper.

Risks: enabling the parent alone builds the core without a probing transport. ISA support can be offered only where port IO exists. Help text is generic and should stay consistent with actual subdriver coverage.

Test signals: build combinations for parent-only, ISA, platform, and both wrappers; verify `HAS_IOPORT=n` hides ISA; and confirm module dependency resolution for wrapper modules against `cc770.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig -->
