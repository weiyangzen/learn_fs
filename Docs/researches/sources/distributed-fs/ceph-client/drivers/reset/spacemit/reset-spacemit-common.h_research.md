# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.h

Purpose: shared type and macro contract for SpacemiT CCU-backed reset controllers.

Important APIs/types/functions: defines `ccu_reset_data`, `ccu_reset_controller_data`, `ccu_reset_controller`, `RESET_DATA()`, and the common `spacemit_reset_probe()` prototype. The data model encodes one reset as register offset plus assert/deassert masks.

Control flow: no direct runtime flow, but SoC drivers use `RESET_DATA()` to build tables consumed by the common probe and ops.

State and persistence: header declares structures used to hold runtime controller state and static reset tables; no independent state.

Dependencies and integration: includes auxiliary bus, regmap, reset-controller, and integer types. It is the compile-time link between K1/K3 table files and common implementation.

Risks and test signals: mask semantics are flexible but easy to misencode when hardware uses clear-to-deassert or separate bits. Compile tests catch signature drift; hardware tests validate each table entry.
