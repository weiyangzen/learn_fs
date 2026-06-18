# sources/distributed-fs/ceph-client/include/soc/sifive/sifive_ccache.h

Purpose: declares notifier registration for SiFive Composable Cache Controller error events and defines error type IDs.

Important APIs/types/functions: exports `register_sifive_ccache_error_notifier()` and `unregister_sifive_ccache_error_notifier()` for `struct notifier_block`, plus `SIFIVE_CCACHE_ERR_TYPE_CE` and `SIFIVE_CCACHE_ERR_TYPE_UE`.

Control flow: clients register a notifier, receive corrected or uncorrected cache error notifications from the ccache driver, and unregister during teardown.

State and persistence: notifier-chain membership is implementation-owned state. Error events are transient hardware interrupts/status reports.

Dependencies and integration: implemented in `drivers/cache/sifive_ccache.c` and consumed by `drivers/edac/sifive_edac.c`.

Risks: notifier lifetime errors can call freed memory or miss ECC events. Correct CE/UE classification is important for EDAC reporting. Test signals include ccache interrupt injection or hardware ECC events, EDAC report validation, and module unload paths.
