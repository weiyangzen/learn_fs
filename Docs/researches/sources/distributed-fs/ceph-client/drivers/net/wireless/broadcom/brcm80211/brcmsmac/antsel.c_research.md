# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.c

Purpose: handles board-level MIMO antenna selection for brcmsmac, translating SROM/board configuration into ucode antenna pattern fields and per-frame antenna config IDs.

Important APIs and functions: `brcms_c_antsel_attach()` detects antenna switch type and availability from SROM and board flags, sets low-driver antenna type, and initializes default/current configs. `brcms_c_antsel_init()` writes default TX/RX antenna selection to SHM. `brcms_c_antsel_antcfg_get()` chooses default, configured, or auto-derived antenna configs for TX descriptors. `brcms_c_antsel_antsel2id()` converts ucode pattern back to selection ID. Internal conversion helpers map 2x3 and 2x4 board layouts through lookup tables.

Control flow: attach selects `ANTSEL_2x3`, `ANTSEL_2x4`, or not available based on `antswitch`, antenna availability, SROM revision, and `BFL2_2X4_DIV`. Init writes default TX and RX SHM fields. Per-frame lookup uses defaults unless caller requests explicit selection and auto mode is enabled.

State and persistence: `struct antsel_info` stores current/default configs, availability, type, and board switch value. Hardware SHM writes persist until reset or reconfiguration.

Dependencies and integration: depends on SSB SPROM data, brcms main/hardware APIs, PHY shim, SHM offsets in `d11.h`, and A-MPDU TX status using `brcms_c_antsel_antsel2id()`.

Risks and test signals: wrong table mapping causes poor RF performance or invalid antenna combinations. SROM edge cases fall back to no auto diversity. Test boards with 2x2, 2x3, and 2x4 layouts, default SHM values, per-frame auto fallback IDs, and invalid SROM configurations.
