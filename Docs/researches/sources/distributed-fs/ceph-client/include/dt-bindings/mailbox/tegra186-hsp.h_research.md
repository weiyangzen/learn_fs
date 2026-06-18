<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h

## Purpose
This header defines NVIDIA Tegra186 HSP mailbox specifier constants for doorbells, shared mailboxes, shared semaphores, arbitrated semaphores, master IDs, and shared-mailbox direction encoding.

## Important APIs, types, and functions
It exports mailbox type constants `TEGRA_HSP_MBOX_TYPE_DB`, `SM`, `SS`, `AS`, the `TEGRA_HSP_MBOX_TYPE_SM_128BIT` flag, doorbell master bits `TEGRA_HSP_DB_MASTER_CCPLEX` and `BPMP`, masks/flags for shared mailbox direction, and helper macros `TEGRA_HSP_SM_RX(x)` and `TEGRA_HSP_SM_TX(x)`.

## Control flow
DTS mailbox specifiers use these constants to identify mailbox kind, master, index, and direction. The Tegra HSP mailbox driver decodes the cells and binds clients such as BPMP IPC to the correct HSP hardware primitive.

## State and persistence
No state is held in the header. Runtime state lives in HSP registers and mailbox framework channels; DTB values persist board/SoC wiring.

## Dependencies and integration points
It integrates with Tegra HSP mailbox drivers, BPMP communication, CCPLEX firmware channels, and shared mailbox/semaphore hardware.

## Risks and test signals
Risks include wrong TX/RX flag use on unidirectional mailboxes, incorrect doorbell master bit, and masking indexes beyond `TEGRA_HSP_SM_MASK`. Test signals include DTS validation, BPMP IPC operation, mailbox loopback or ping tests, and driver decode traces for each mailbox type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h -->
