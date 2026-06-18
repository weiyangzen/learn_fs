# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.h

Purpose: public header for brcmsmac AI/BCMA chip utility state, constants, and exported helper functions.

Important APIs and types: defines core sizes, maximum cores, DMA translation constants, chipcommon clock-control bits, GPIO conventions, and `struct si_pub` public chip metadata. `struct si_info` embeds `si_pub` first and adds BCMA bus, PCI bus, and chip status. Exports `ai_core_cflags()`, `ai_attach()`, `ai_detach()`, `ai_cc_reg()`, clock-control helpers, `ai_deviceremoved()`, and `ai_epa_4313war()`. Inline accessors return chip, board, PMU, and chipcommon fields.

Control flow: no implementation, but documents the handle model: callers obtain `si_pub` from attach, pass it to utility routines, and detach when done.

State and persistence: describes in-memory chip metadata and register manipulation APIs. Register writes through these helpers affect hardware state.

Dependencies and integration: depends on Linux BCMA and brcmsmac `types.h`. Used by main, PMU, PHY, and board setup code to avoid open-coding chipcommon access.

Risks and test signals: struct-first embedding is an ABI invariant for container conversions. Constants must match hardware documentation. Build tests catch declaration drift; runtime tests should validate chip metadata and clock behavior on each supported board family.
