# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.h

Purpose: Declares the DFS radar PHY-error processing entry point and provides a no-op stub when certified DFS support is not built.

Important APIs: `ath9k_dfs_process_phyerr(struct ath_softc *sc, void *data, struct ath_rx_status *rs, u64 mactime)` is available under `CONFIG_ATH9K_DFS_CERTIFIED`.

Control flow: RX PHY error paths can call this unconditionally when included; the implementation is compiled only for certified DFS builds, otherwise the inline stub drops the event.

State/persistence: No direct state. The implementation uses `ath_softc` DFS detector and debug stats.

Dependencies/integration: Includes `../dfs_pattern_detector.h` and relies on ath softc/RX status declarations from including contexts.

Risks: Feature-disabled builds silently ignore radar processing, so regulatory behavior depends on build configuration and hardware flags. Callers must still ensure RX filters are configured appropriately.

Test signals: Compile with and without `CONFIG_ATH9K_DFS_CERTIFIED`, radar RX path invocation, and absence of unresolved symbols in non-DFS builds.
