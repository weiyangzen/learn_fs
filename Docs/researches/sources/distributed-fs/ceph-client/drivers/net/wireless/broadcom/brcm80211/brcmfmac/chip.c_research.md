# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c

Purpose: Implements brcmfmac chip/backplane discovery and low-level core control. It reads ChipCommon, SB, and AI/BCMA register spaces through `brcmf_buscore_ops`, builds a core list, validates CPU/RAM topology, computes RAM layout, and exposes passive/active transitions used around firmware loading.

Important APIs/types/functions: `brcmf_chip_attach()`, `brcmf_chip_detach()`, `brcmf_chip_get_raminfo()`, core lookup helpers, `brcmf_chip_set_passive()`, `brcmf_chip_set_active()`, and `brcmf_chip_sr_capable()`. Private `brcmf_chip_priv` owns bus ops, core list, and interconnect-specific callbacks. Internal code covers SB/AI core reset/disable/is-up, AI DMP EROM scanning, SOCRAM/SYSMEM/TCM sizing, PMU lookup, and chip-specific RAM-base tables.

Control flow: Attach validates bus callbacks, prepares the bus, recognizes SB vs AI chips, adds fixed SB cores or scans AI EROM, verifies core presence, forces passive state, optionally invokes bus reset, then fills RAM info. Active/passive paths dispatch by CPU core type: CM3, CR4, or CA7.

State and persistence behavior: Runtime state lives in allocated chip/core objects and hardware registers. No filesystem persistence.

Dependencies and integration points: Used by bus probes, firmware loaders, and power-management logic. Depends on BCMA/SSB register definitions, Broadcom hardware ids, ChipCommon offsets, and debug logging.

Risks: Hardware sequencing is fragile. Unknown CR4/CA7 RAM base fails probe. EROM parsing can skip malformed components. RAM sizing has chip-specific retention overrides. Dual-D11 reset is special-cased.

Test signals: Probe logs should show chip, cores, PMU, and RAM. Test SB BCM4329, AI CM3/CR4/CA7, firmware boot after passive/active, unknown chip rejection, and SR-capability detection.
