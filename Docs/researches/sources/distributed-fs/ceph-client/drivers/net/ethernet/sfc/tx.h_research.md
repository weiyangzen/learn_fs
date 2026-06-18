# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.h

Purpose: provides internal TX declarations and checksum queue-type selection for SFC.

Important APIs: declares `efx_tx_limit_len()` and defines `efx_tx_csum_type_skb()`. The inline helper maps `CHECKSUM_PARTIAL` SKBs to no checksum, outer checksum, inner checksum, or combined inner/outer checksum queue types depending on encapsulation and GSO tunnel checksum requirements.

State and integration: no local state. It integrates `tx.c`, NIC-specific TX queue lookup, and advertised offload features by selecting a queue type matching what the skb requires.

Risks and tests: if feature advertising and this helper diverge, `efx_hard_start_xmit()` may not find a suitable queue. Test encapsulated and non-encapsulated checksum SKBs, UDP tunnel checksum GSO, and no-offload SKBs.
