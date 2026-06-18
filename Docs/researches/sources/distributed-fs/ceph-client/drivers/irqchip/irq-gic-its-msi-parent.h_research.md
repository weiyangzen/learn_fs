# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.h

## Purpose
Declares GIC ITS MSI parent operation tables for GICv3 and GICv5 users.

## Important APIs, Types, and Functions
The header exports `gic_v3_its_msi_parent_ops` and `gic_v5_its_msi_parent_ops` as `extern const struct msi_parent_ops`.

## Control Flow
No runtime logic exists in the header. Consumers include it to pass the appropriate parent ops when creating ITS-backed MSI parent domains.

## State and Persistence
No state is declared. The referenced const operation tables live in `irq-gic-its-msi-parent.c`.

## Dependencies and Integration Points
Depends on `struct msi_parent_ops` being available through including translation units. It is a narrow integration boundary for GIC ITS MSI setup.

## Risks and Test Signals
Risks are limited to declaration/definition mismatch or missing include coverage. Test signals are successful linkage and creation of GICv3/GICv5 ITS MSI domains using the declared symbols.
