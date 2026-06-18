# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_status.h

Purpose: defines the shared BFA status code enum returned by IOC, flash, CEE, diagnostics, firmware, and higher-level management APIs.

Important APIs/types/functions: `enum bfa_status` enumerates `BFA_STATUS_OK` through `BFA_STATUS_MAX`, including common errors (`FAILED`, `EINVAL`, `ENOMEM`, `DEVBUSY`, `IOC_FAILURE`, `IOC_NON_OP`), flash errors, link/port errors, CNA/team/VLAN errors, boot/firmware errors, and many domain-specific management statuses. `enum bfa_eproto_status` defines protocol error sub-status values.

Control flow: no executable flow. Other modules switch on or return these values to report asynchronous and synchronous API outcomes. For this subset, `bfa_cee.c` returns `IOC_FAILURE`/`DEVBUSY` and callback statuses, while `bfa_ioc.c` returns or stores IOC/flash-related statuses.

State and persistence behavior: no state. Numeric values are an ABI-like contract across driver modules, firmware-adjacent code, and any tooling that decodes status numbers.

Dependencies and integration points: standalone header included by `bfa_defs.h` and then widely by IOC/CEE/flash definitions and implementations.

Risks: renumbering values can break log decoding, userspace tooling, or firmware-aligned assumptions. Comments mention auto-generated error messages, so comment formatting may matter to external generators even though no generator is present in this file.

Test signals: compile-time coverage from all users, plus runtime paths returning expected values for busy, invalid length, IOC non-operational, firmware mismatch, and flash failures.
