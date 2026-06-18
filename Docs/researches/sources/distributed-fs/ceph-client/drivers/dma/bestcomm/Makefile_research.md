# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Makefile

Purpose: Build description for the BestComm core and task helper modules.

Important targets: `bestcomm-core-objs` combines `bestcomm.o` and `sram.o`; `bestcomm-ata-objs` combines `ata.o` with `bcom_ata_task.o`; `bestcomm-fec-objs` combines `fec.o`, RX microcode, and TX microcode; `bestcomm-gen-bd-objs` combines `gen_bd.o` with generic RX/TX microcode.

Control flow: Kbuild includes each composite object only when the matching `CONFIG_PPC_BESTCOMM*` symbol is enabled. The microcode C arrays are linked into the same module/object as the wrapper that loads them.

State and persistence: No runtime state. Its effect is persisted only in build outputs and module composition.

Dependencies/integration: Paired with the sibling Kconfig and the exported symbols in BestComm wrappers. The object grouping keeps generated task images private to their task modules while exposing wrapper APIs to users.

Risks: If a microcode object is omitted, reset/init wrappers will fail at link time because they reference external task arrays. If a wrapper is built separately from its task image, module loading would fail. Ordering is simple and relies on Kbuild composite object semantics.

Test signals: `make drivers/dma/bestcomm/` for each config combination, `modinfo` for module composition, and link checks for task-array references.
