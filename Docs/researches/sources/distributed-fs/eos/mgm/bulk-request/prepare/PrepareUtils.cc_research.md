## sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.cc

Purpose: converts XRootD prepare option bitmasks into a readable comma-separated string for logging.

Important flow: masks priority with `Prep_PMASK`, maps `Prep_PRTY0..3`, maps send flags via mask `12`, appends flags for `WMODE`, `STAGE`, `COLOC`, `FRESH`, and under supported XRootD versions `CANCEL`, `QUERY`, and `EVICT`.

State/dependencies: stateless; depends on XRootD version/prepare constants. Risks include the hard-coded send mask and version-dependent output differences. Tests should exercise representative bit combinations, unknown priority/send values, and XRootD-version-gated flags.
