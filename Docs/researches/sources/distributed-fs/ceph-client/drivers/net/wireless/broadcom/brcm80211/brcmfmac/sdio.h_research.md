# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.h

## Purpose
`sdio.h` declares the SDIO bus/device interface, Broadcom SDIO register constants, function accessors, low-level transfer routines, device state enum, and probe/remove/interrupt/sleep hooks shared between `sdio.c` and lower-level SDIO support code.

## Important APIs, types, and functions
- Register constants cover SDIO CCCR vendor registers, function 1 misc registers, SB/OCP address windowing, function interrupt bits, KSO/SleepCSR, watermark/MES busy controls, and watchdog poll interval.
- `enum brcmf_sdiod_state` distinguishes `BRCMF_SDIOD_DOWN`, `BRCMF_SDIOD_DATA`, and `BRCMF_SDIOD_NOMEDIUM`.
- `struct brcmf_sdio_dev` is the shared SDIO device object: function 1/2 handles, saved backplane window, chipcommon core, `struct brcmf_sdio *bus`, Linux device, `brcmf_bus`, module settings, IRQ flags/lock, SG capabilities/table, request-size limits, firmware/NVRAM/CLM names, WoWL and power-management flags, state/freezer, and retained CLM firmware.
- `struct sdpcmd_regs` maps SDIO core register layout for offset calculations used by `SD_REG()` in `sdio.c`.
- Accessor macros wrap function 0 and function 1 byte reads/writes.
- Declared low-level operations include `brcmf_sdiod_readl/writel()`, packet/buffer send/receive, receive chain, RAM read/write, abort, SG allocation, state/freezer helpers, `brcmf_sdiod_probe/remove()`, `brcmf_sdio_probe/remove()`, `brcmf_sdio_isr()`, watchdog timer, WoWL config, sleep, and DPC trigger.

## Control flow
The header defines the boundary between the high-level SDPCM bus logic in `sdio.c` and lower-level SDIO device operations. Platform/SDIO probe code constructs `brcmf_sdio_dev`, calls `brcmf_sdiod_probe()` and `brcmf_sdio_probe()`, routes interrupts into `brcmf_sdio_isr()`, and later calls remove. `sdio.c` calls low-level buffer/RAM/register helpers declared here to perform CMD52/CMD53 traffic.

## State and persistence behavior
`struct brcmf_sdio_dev` persists for the SDIO function device lifetime and carries both low-level transport state and pointers to high-level bus state. Register constants describe device-side state modified for the current session. Firmware name buffers and retained `clm_fw` persist until removal or blob handoff.

## Dependencies and integration points
The header depends on Linux skb and firmware types plus `firmware.h`. It integrates SDIO function-driver code, chipcore access, firmware setup, interrupt registration, freezer support, and the high-level bus backend.

## Risks and edge cases
- `struct sdpcmd_regs` must match hardware layout; bad offsets affect interrupt masks, mailboxes, and frame control.
- Macros directly call SDIO core functions and assume the correct host claim context is held by callers where required.
- `brcmf_sdio_dev` contains many ownership-sensitive raw pointers and flags; remove paths must coordinate IRQ, freezer, firmware, SG table, and bus state lifetimes.
- Register masks/constants are chip-generation sensitive, especially KSO, CMD14, and address-window behavior.

## Test signals
Compile coverage across `sdio.c` and low-level SDIO files is necessary. Runtime signals include correct register access, interrupt registration/unregistration, state transitions, SG allocation fallback, RAM read/write firmware download, abort behavior, freezer transitions, sleep/wake, and clean remove with function 1/2 devices.
