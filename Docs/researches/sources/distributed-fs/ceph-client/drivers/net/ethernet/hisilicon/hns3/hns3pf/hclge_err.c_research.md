# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.c

## Purpose

`hclge_err.c` implements PF hardware error interrupt configuration, detection, logging, clearing, and reset escalation for HNS3. It covers common HNS blocks, MAC tunnel interrupts, MSI-X reported errors, RAS nonfatal errors, RoCEE RAS errors, firmware-summarized all-error logs, and VF queue-error recovery.

## Important APIs, Tables, And Functions

The exported functions are `hclge_config_mac_tnl_int()`, `hclge_config_nic_hw_error()`, `hclge_config_rocee_ras_interrupt()`, `hclge_handle_hw_ras_error()`, `hclge_handle_hw_msix_error()`, `hclge_handle_mac_tnl()`, `hclge_handle_all_hns_hw_errors()`, `hclge_find_error_source()`, `hclge_handle_occurred_error()`, `hclge_handle_error_info_log()`, and `hclge_handle_vf_queue_err_ras()`.

Large `hclge_hw_error` tables map interrupt status masks to log strings and reset levels for IMP TCM, CMDQ, TQP, MSI-X SRAM, IGU/EGU, NCSI, PPP, TM, QCN, MAC AFIFO/TNL, PPU, SSU, and RoCEE overflow conditions. Module/type tables decode firmware all-error summaries into human-readable module and error-type names. Register-info tables describe extra SSU/IGU/RPU/general DFX registers printed when certain module errors occur.

## Control Flow

Enable/disable flow starts at `hclge_config_nic_hw_error()`: it toggles vector0 all-MSI-X error delivery through MMIO, then iterates `hw_blk[]` and calls per-block command functions to configure IGU/EGU, PPP, SSU, PPU, TM, COMMON, and MAC error interrupts. `hclge_config_rocee_ras_interrupt()` separately handles RoCEE on supported V2+ RoCE devices and clears pending RoCEE RAS state when enabling.

RAS handling starts in `hclge_handle_hw_ras_error()`. It refuses recovery before service initialization, reads `HCLGE_RAS_PF_OTHER_INT_STS_REG`, clears `ae_dev->hw_err_reset_req` for relevant nonfatal bits, handles HNS RAS via `hclge_handle_all_ras_errors()`, handles RoCEE RAS via `hclge_handle_rocee_ras_error()`, and returns `PCI_ERS_RESULT_NEED_RESET` if any reset bit was requested. HNS RAS handling queries firmware-reported MPF/PF BD counts, allocates descriptors, reads and logs MPF and PF RAS registers, sets reset bits from tables, reports selected hardware errors, and reuses the descriptors to clear interrupts.

MSI-X handling starts in `hclge_handle_hw_msix_error()`, which requires service initialization and then queries MPF/PF BD counts. MPF MSI-X handling logs MAC AFIFO/TNL and selected PPU errors; PF MSI-X handling logs SSU, PPP, and PPU PF errors and treats `over_8bd_no_fe` specially by querying vport/queue details and requesting either VF notification or PF reset. Both paths clear their interrupt status through `hclge_clear_hw_msix_error()`, then `hclge_handle_mac_tnl()` records MAC tunnel interrupt status and time into `hdev->mac_tnl_log`.

`hclge_handle_error_info_log()` queries firmware's all-error BD count and data, converts descriptor data to CPU-endian words, decodes nested summary/module/type/register records, logs register values, optionally queries extra module registers, sets reset bits, and marks `HNAE3_VF_EXP_RESET` when supported VF-caused errors are detected. `hclge_handle_vf_queue_err_ras()` consumes that VF reset request, queries a VF fault bitmap, resets TQPs, informs affected VFs, and clears broader reset requests if VF-local recovery succeeded.

## State And Persistence Behavior

The file mutates `ae_dev->hw_err_reset_req`, hardware interrupt enable registers, hardware interrupt status through query-clear commands, `hdev->mac_tnl_log`, and VF reset state through mailbox/reset notification helpers. Error logs persist only through kernel logs and debugfs-visible MAC tunnel FIFO entries. Reset request bits persist until consumed by the reset/service path.

## Dependencies And Integration Points

It depends on command descriptors, debug command send support, HNS3 MMIO helpers, PCI error recovery types, RoCE capability checks, reset notification helpers, VF/vport helpers, and HNAE3 reset enums. `hclge_main.c` enables NIC hardware errors during initialization and reset recovery, disables them during teardown, invokes MSI-X/RAS handlers from service or interrupt paths, and exposes `handle_hw_ras_error` through AE ops.

## Risks

Error decoding is highly firmware-layout-dependent: descriptor indices, status masks, BD minimums, and nested all-error records must match firmware. Several handlers allocate descriptor arrays sized by firmware-reported counts; count validation protects minimums, but unexpectedly large values still create memory pressure. Logging and clearing are coupled: command failures can leave interrupts uncleared and retriggering. Some errors request global reset while others request function or VF reset; incorrect table reset levels can either over-reset or under-recover. VF-local recovery relies on accurate bitmaps and valid vport lookup. `hclge_handle_error_type_reg_log()` indexes module/type tables through sentinel-like defaults, so unknown module/type combinations need careful bounds behavior.

## Test Signals

Test interrupt enable/disable command payloads, service-init gating, RAS and MSI-X query-clear failure paths, firmware-reported invalid BD counts, RoCEE AXI/ECC/overflow logs, `over_8bd_no_fe` PF versus VF handling, all-error summary parsing with malformed lengths, VF fault bitmap recovery, MAC tunnel FIFO logging, and reset request bit outcomes. Fault-injection or firmware command mocking is needed for meaningful coverage.
