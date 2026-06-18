# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.h

Purpose: defines the MACsec hardware programming model used by `mscc_macsec.c`: security-association flow limits, transformation control bits, destination ports, drop/action modes, validation modes, CSR target banks, the `struct macsec_flow` software representation, and register/bitfield macros for the MACsec classifier, flow controller, context records, counters, interrupts, and MTU checks.

Important APIs/types:
- `MSCC_MS_MAX_FLOWS` caps each ingress and egress bank at 16 SAM entries.
- `enum macsec_bank` maps abstract block names (`MACSEC_INGR`, `MACSEC_EGR`, `HOST_MAC`, `LINE_MAC`, `FC_BUFFER`, processor banks) to the target IDs consumed by the CSR accessors.
- `struct macsec_flow` is the key software object for one hardware flow. It stores the list node, bank, hardware index, association number, priority, ingress or egress SA pointer, match flags for SCI/tagged/untagged/EtherType, optional EtherType, action flags, destination port, and whether transformation context has been installed.
- The `CONTROL_*` and `CTRYPTO_ALG_*`/`AUTH_ALG_*` macros encode transformation record word 0 for AES-CTR plus AES-GHASH MACsec operation.
- Register macros such as `MSCC_MS_SAM_MISC_MATCH(x)`, `MSCC_MS_SAM_MASK(x)`, `MSCC_MS_SAM_FLOW_CTRL(x)`, and `MSCC_MS_XFORM_REC(x, y)` provide indexed access to classifier and transformation tables.

Control flow enabled by this header: callers build a SAM match word from `MSCC_MS_SAM_MISC_MATCH_*`, a mask word from `MSCC_MS_SAM_MASK_*`, and an action word from `MSCC_MS_SAM_FLOW_CTRL_*`; then they activate entries through `MSCC_MS_SAM_ENTRY_SET1` or clear them through `MSCC_MS_SAM_ENTRY_CLEAR1`. Transformation records are 32-word-spaced with `MSCC_MS_XFORM_REC()`, allowing the C file to serialize control, context ID, encryption key, derived auth key, PN/replay window, SCI, and zero fill. Default non-match handling is configured with `MSCC_MS_SAM_NM_FLOW_NCP` and `MSCC_MS_SAM_NM_FLOW_CP`.

State and persistence: this header does not allocate state itself, but its `struct macsec_flow` layout defines the in-memory state kept under `vsc8531_private.macsec_flows`. The hardware register defines describe state that persists in the PHY until reset or explicit writes: enabled clocks, SAM entries, flow-control words, counter mode, MTU limits, context records, and interrupt masks/status.

Dependencies and integration points: includes `<net/macsec.h>` for MACsec SA pointer types. It is included by `mscc_macsec.c` and indirectly tied to `mscc.h`, whose private structure stores flow lists and SecY state behind `CONFIG_MACSEC`. Many macros are paired with register-bank access logic in `vsc8584_macsec_phy_read/write()`.

Risks and edge cases:
- Bit definitions overlap intentionally across ingress and egress interpretations, for example `MSCC_MS_SAM_FLOW_CTRL_PROTECT_FRAME` and `MSCC_MS_SAM_FLOW_CTRL_REPLAY_PROTECT` both use bit 16. Callers must use them only with the correct bank.
- The typo-style names `CTRYPTO_ALG_*` and `AUTH_ALG_AES_GHAS` are part of the local API; renaming requires coordinated code changes.
- Wide shift macros accept unbounded arguments, so callers must validate values before shifting into hardware fields.
- Register constants are dense and hardware-specific; a single incorrect address affects security behavior more than ordinary link setup.

Test signals: compile coverage under `CONFIG_MACSEC=y`; static analysis for field-width overflow; MACsec packet tests for each flow action/validation mode; interrupt tests for `MACSEC_INTR_CTRL_STATUS_ROLLOVER`; and cross-check against the VSC8584 MACsec register map for table offsets and bit positions.
