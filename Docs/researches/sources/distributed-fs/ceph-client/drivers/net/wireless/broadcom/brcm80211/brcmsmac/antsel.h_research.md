# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/antsel.h

Purpose: exposes the brcmsmac antenna selection module interface.

Important APIs: declares attach/detach, hardware init, antenna config retrieval, and conversion from ucode `mimo_antsel` pattern to antenna selection ID.

Control flow: main driver attaches the module during setup, calls init when programming hardware, asks for antenna configs when building TX descriptors, and detaches on shutdown.

State and persistence: hides `struct antsel_info` internals in `antsel.c`. Hardware state is SHM-programmed by implementation calls.

Dependencies and integration: depends on brcms internal types and board configuration parsed elsewhere. It is consumed by main TX/PHY/A-MPDU logic.

Risks and test signals: incorrect caller ordering, especially using config retrieval before attach/init, can produce default IDs or null dereferences. Build and runtime tests should cover no-antenna-selection boards and auto-selection capable boards.
