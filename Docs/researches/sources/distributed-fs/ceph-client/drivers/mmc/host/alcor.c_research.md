# sources/distributed-fs/ceph-client/drivers/mmc/host/alcor.c

## Purpose
`alcor.c` is a Linux MMC host driver for Alcor Micro AU6601/AU6621 PCI-attached SD card controller functions. It is explicitly reverse-engineered from observed hardware behavior and a vendor driver rather than public documentation, so much of the register programming is conservative and sequence-sensitive. The driver exposes the controller through `struct mmc_host_ops` and depends on the companion Alcor PCI core for MMIO helpers and register definitions.

## Important APIs, Types, and Functions
The central state object is `struct alcor_sdmmc_host`, which stores the active `mmc_request`, command/data pointers, DMA/PIO scatterlist state, delayed timeout work, IRQ status, current power mode, and a `cmd_mutex` serializing request, IRQ-thread, timeout, and IOS paths. `enum alcor_cookie` records whether MMC core pre-request DMA mapping was skipped, pre-mapped, or mapped.

Key operations are `alcor_request`, `alcor_pre_req`, `alcor_post_req`, `alcor_set_ios`, `alcor_get_cd`, `alcor_get_ro`, `alcor_card_busy`, and `alcor_signal_voltage_switch`, wired into `alcor_sdc_ops`. Transfer helpers include `alcor_send_cmd`, `alcor_prepare_data`, `alcor_trigger_data_transfer`, `alcor_trf_block_pio`, `alcor_data_set_dma`, `alcor_finish_data`, and `alcor_request_complete`. Probe/remove/PM are handled by `alcor_pci_sdmmc_drv_probe`, `alcor_pci_sdmmc_drv_remove`, `alcor_pci_sdmmc_suspend`, and `alcor_pci_sdmmc_resume`.

## Control Flow and State
Probe allocates an MMC host, disables controller interrupts, requests a shared threaded IRQ, initializes the mutex and timeout work, configures MMC limits/capabilities, and performs hardware init. Requests enter `alcor_request`, are rejected with `-ENOMEDIUM` if card-detect is false, otherwise `alcor_send_cmd` writes opcode/argument/response control and arms a delayed timeout. Command completion can be handled in the hard IRQ fast path when all needed work is simple; otherwise the IRQ masks SD interrupts, records status, and wakes `alcor_irq_thread`.

Data transfers are PIO by default or page-at-a-time DMA for large aligned CMD18/CMD25 transfers. DMA is only selected in `pre_req` when every segment is 4096 bytes, segment offsets are zero, block size is word-aligned, and the request is large enough. The hardware cannot scatter-gather directly, so each DMA-end interrupt advances to the next page with `alcor_data_set_dma`. PIO uses `sg_mapping_iter` and transfers one block per buffer-ready interrupt. `alcor_finish_data` sends CMD12 for open-ended or failed multiblock transfers, otherwise completes the request.

## State and Persistence Behavior
The driver persists only volatile kernel and hardware state: current request pointers, SG iterators, cached power mode, IRQ snapshot, and controller registers. No durable data is stored by this file. Power sequencing and hardware initialization write multiple unexplained registers, reset command/data engines, set pins to input, configure card detect, and later uninitialize by masking IRQs, resetting engines, powering off VDD, and clearing voltage options.

## Dependencies and Integration Points
This file integrates with Linux MMC core, DMA mapping, scatterlist iteration, platform-driver binding via `DRV_NAME_ALCOR_PCI_SDMMC`, delayed work, threaded IRQs, and Alcor PCI helpers from `<linux/alcor_pci.h>`. It advertises SD high-speed and UHS modes, 4-bit data, no SDIO, a 3.3 V OCR, and request/segment limits matching hardware and vendor-driver behavior.

## Risks and Test Signals
Risks are concentrated around undocumented register sequences, interrupt masking losing status updates, strict DMA assumptions, the 240-sector request cap, timeout race handling, and card removal during active requests. Test signals include successful probe and `mmc_add_host`, card insertion/removal detection, PIO and DMA reads/writes across aligned and unaligned SG layouts, multiblock stop handling, voltage switch behavior, suspend/resume, timeout recovery, and absence of leaked DMA mappings after `post_req`.
