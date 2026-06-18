
# sources/distributed-fs/ceph-client/include/linux/nvme.h

Purpose: provides the core NVMe specification vocabulary for kernel code: register offsets, bit fields, identify/log data structures, admin/I/O/fabrics commands, authentication payloads, completion/status definitions, and helper macros.

Important APIs/types/functions: constants define NQN/address sizes, discovery subsystem name, queue depths, register offsets, controller capabilities, CC/CSTS bits, CMB/PMR fields, feature/log IDs, status codes, and version helpers. Structures model identify controller/namespace data, ZNS/NVM command-set data, SMART/FW/effects/ANA/zone/FDP/reservation logs, SGL/PRP data pointers, all major I/O/admin/fabrics command layouts, discovery log entries, DH-HMAC-CHAP auth messages, completion entries, and persistent reservation payloads. Helpers include LBA format extraction, command opcode symbolic formatting, `nvme_is_fabrics()`, `nvme_is_write()`, verbose opcode/status string fallbacks, and version field extraction.

Control flow: host, target, and transport code fill `struct nvme_command` unions for admin, I/O, or fabrics operations; controllers return `struct nvme_completion`; identify/log commands transfer fixed 4096-byte or variable payloads; fabrics connect/auth/property commands use the same capsule model over RDMA/TCP/FC. Helpers classify command type and choose diagnostic strings.

State and persistence: this header stores no runtime state. Many structures describe persistent device data or controller state as reported by hardware, while command/completion structures are transient wire/MMIO/queue entries.

Dependencies and integration points: depends on bit helpers, fixed-width types, UUIDs, trace-print symbolic macros from includers, and transport headers. It is the central integration contract for NVMe PCI, fabrics, target, multipath/ANA, reservations, authentication, ZNS, FDP, and block-layer code.

Risks and test signals: risks include spec drift, wrong endian annotations, structure size/layout regressions, conflicting command/status values across command sets, variable-length array bounds, and helper classification mistakes for fabrics write direction. Test signals include static asserts for 4096-byte identify structures, nvme-cli identify/log comparisons, tracepoint opcode/status decoding, fabrics connect/auth tests, ZNS/FDP/reservation command tests, and ABI/layout compile checks across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme.h -->
