# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcmsdh.c

## Purpose
Implements brcmfmac's SDIO host/device interface. It registers the SDIO driver, probes/removes two-function devices, configures block sizes and interrupts, provides function/backplane reads and writes, transfers skbs with optional scatter-gather, supports firmware RAM access, and handles suspend/resume/WOWL/freezer behavior.

## Important APIs, Types, and Functions
Key public routines include `brcmf_sdiod_intr_register()`, `brcmf_sdiod_intr_unregister()`, `brcmf_sdiod_change_state()`, `brcmf_sdiod_readl()`, `brcmf_sdiod_writel()`, `brcmf_sdiod_recv_buf()`, `brcmf_sdiod_recv_pkt()`, `brcmf_sdiod_recv_chain()`, `brcmf_sdiod_send_buf()`, `brcmf_sdiod_send_pkt()`, `brcmf_sdiod_ramrw()`, `brcmf_sdiod_abort()`, `brcmf_sdiod_sgtable_alloc()`, freezer helpers, `brcmf_sdiod_probe()`, `brcmf_sdiod_remove()`, `brcmf_sdio_wowl_config()`, `brcmf_sdio_register()`, and `brcmf_sdio_exit()`. Static SDIO driver callbacks cover probe, remove, suspend, and resume.

## Control Flow, State, and Persistence
Probe ignores function 1 callbacks except to keep the card alive, consumes function 2, allocates `brcmf_bus` and `brcmf_sdio_dev`, records func1/func2, saves ACPI power flags, sets state DOWN, configures F1/F2 block sizes, enables F1, attaches the freezer, calls lower `brcmf_sdio_probe()`, and marks the host non-removable while forbidding runtime PM power-off. Interrupt registration chooses OOB GPIO IRQs or in-band SDIO IRQs, configures CCCR interrupt bits for OOB, and records request flags. Backplane 32-bit access caches the SB window in `sdiodev->sbwad`. Packet transfers use simple CMD53 for single packets or manual MMC scatter-gather requests with fallbacks for broken SG hosts. State includes SDIO functions, bus interface, current SDIOD state, cached backplane window, IRQ request/enabled flags, SG table/capabilities, freezer counters/completion, WOWL state, and saved ACPI power-manageable flags.

## Dependencies and Integration Points
Depends on Linux MMC/SDIO, PM runtime/sleep, ACPI, cfg80211 coredump hook, brcmfmac bus/core/sdio lower layer, chipcommon addressing, firmware vendor ids, skbuff and scatterlist helpers. The SDIO ID table maps Broadcom/Cypress device IDs to WCC/CYW firmware vendor IDs.

## Risks and Test Signals
Risks include host-claim imbalance, OOB IRQ wake misconfiguration, SG segmentation errors, backplane window cache corruption, ENOMEDIUM state transitions, freezer deadlock during suspend, ACPI power flag restoration, and reprobe after power-off resume. Test SDIO probe/remove, OOB and in-band IRQs, glommed RX/TX with and without SG, firmware RAM download/readback, WOWL suspend/resume, power-off suspend/resume reprobe, card removal, and runtime PM interactions.
