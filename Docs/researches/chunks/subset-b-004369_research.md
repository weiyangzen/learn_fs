# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_reg.h lines 4703-7778

## Scope

This chunk is the final large register-definition slice of `bnx2x_reg.h`. It covers timer, SDM, SEM, CM, MAC, PCIe, attention, MDIO/PHY, IGU, CDU, idle-check, and CRC helper definitions used by the Broadcom NetXtreme II `bnx2x` Ethernet driver. Most content is preprocessor constants for memory-mapped GRC registers, MAC subregister offsets, MDIO Clause 22/45 registers, bit masks, queue/window ranges, and hardware attention bits. The only executable code in this chunk is the inline CRC-8 helper at the end.

The chunk does not define driver structs or high-level Linux APIs. Its API surface is the symbol namespace consumed by `bnx2x_main.c`, `bnx2x_link.c`, `bnx2x_cmn.c`, `bnx2x_sriov.c`, `bnx2x_self_test.c`, and related init/header code.

## Register And Constant Families

- Lines 4703-4733: `TM_REG_*` timer block registers for linear timer address programming, scan timeout, context region, timer tick sizing, interrupt status/mask, and parity status/mask/clear.
- Lines 4734-4815, 5216-5307, and 5767-5860: `TSDM_REG_*`, `USDM_REG_*`, and `XSDM_REG_*` SDM blocks. These publish aggregate interrupt event/T/mode slots, completion and queue counter RAM start addresses, PXP credit, enable gates, parser/PXP FIFO-empty signals, timer ticks, statistics counters, interrupt registers, and parity registers.
- Lines 4816-4950, 5308-5442, and 5861-5996: `TSEM_REG_*`, `USEM_REG_*`, and `XSEM_REG_*` SEM micro-engine registers. These cover thread arbitration elements, time-slot schemes, FIC/passive-buffer disables, fast memory, PRAM/passive-buffer memory windows, sleeping/free thread state, message counters, interrupt/parity registers, and VF/PF error reset selectors.
- Lines 4951-5189 and 5446-5727 plus 5763-5766: `UCM_REG_*` and `XCM_REG_*` connection-manager registers. They define AG context indirect windows, CDU/STORM/TM/QM/NIG/PBF/SEM/DORQ/SDM interface enables, WRR weights, initial credits, event IDs and CM headers, STORM context load sizes, physical queue mapping, message length mismatch latches, AG context region sizing, queue/counter decision registers, and XX protection CAM/table/descriptor state.
- Lines 5190-5215 and 5728-5762: UMAC/XMAC register offsets and bits for enable/reset, loopback, flow-control pause/PFC, source MAC address, EEE timers/control, maximum frame size, and link-fault status clear/masking.
- Lines 5997-6009: MCP/NVM bit definitions for access locking, NVM read/write enable, address, command sequencing, done/doit/first/last/write bits, flash size, and software arbitration.
- Lines 6010-6104: BIGMAC/BIGMAC2 and EMAC register offsets/bits for RX/TX control, max sizes, pause/PFC, MDIO command/mode/status, LED overrides, port mode, half duplex, resets, statistics counters, MTU jumbo enable, promiscuous mode, VLAN preservation, and flow control.
- Lines 6105-6200: MISC GPIO/SPIO, reset-register, and hardware-lock constants. These map board pins, output/floating modes, interrupt set/clear positions, reset bits for core blocks/MACs/PHY muxes, and shared firmware lock resource IDs.
- Lines 6201-6326: AEU attention-bit maps, reserved/general attention assignments, storm/MCP fatal assertion bits, link-sync attention bits, latched GRC/MCP parity attention bits, and `GENERAL_ATTEN_WORD()` / `GENERAL_ATTEN_OFFSET()` helpers.
- Lines 6327-6377: `GRCBASE_*` base addresses for the major device blocks, used with generated register offsets and by firmware/chipsim-compatible address calculations.
- Lines 6380-6555: PCI configuration offsets, command/status/capability bit masks, MSI/MSI-X fields, BAR/GRC access windows, BAR size encoding, power-management state bits, VF MSI-X/PF-VF assignment config, and BAR internal-memory offsets for storm memories, IGU, doorbells, and ME registers.
- Lines 6556-6803: PXPCS transaction-layer PCIe error/status bits for functions 0/1 and 2-7, duplicated BAR offsets, and ME PF/VF identity fields.
- Lines 6804-6823: VF-visible PXP address windows for IGU, USDM queues, CSDM global registers, and doorbells.
- Lines 6825-7524: MDIO/PHY register banks and bit definitions for CL73/CL37 autonegotiation, RX/TX lane equalization and drivers, XGXS lane swap/unicore modes, GP link/speed status, parallel detect, SerDes digital controls/status, over-1G user pages, BAM next pages, combo IEEE MII control/status/advertisement, PMA/PCS/AN/WIS/XS device addresses, SFP two-wire access, BCM8726/8727/8073/7101/8481/84823/84833/84858 PHY-specific control registers, PHY mailbox commands/statuses, Warpcore Clause 45 registers, CL72/CL82/KR/KR2/FEC/TX FIR controls, GPHY 54618SE IDs, interrupts, EEE, expansion, shadow LED/autodetect registers.
- Lines 7526-7624: IGU command-address space, command register offsets, MSI-X/PBA ranges, interrupt-ack and producer-update ranges, attention command slots, PF/VF configuration bits, doorbell/status-block segment counts, FID encoding, and mapping-memory field masks.
- Lines 7626-7642: CDU context-region constants and macros for computing context validation bytes from CID/region/type via CRC-8.
- Lines 7644-7718: idle-check register list for PXP/PXP2 errors, PBF task/credit counters, QM byte/VOQ credits and queue mapping, GRC timeout FID, and NIG ingress/egress FIFO-empty signals.
- Lines 7720-7778: `calc_crc8()`, an inline Verilog-derived CRC-8 implementation for polynomial bits 0-1-2-8.

## Important API Surface

The exported surface is the macro namespace itself:

- `*_REG_*` address constants are passed to `REG_RD()`, `REG_WR()`, `REG_RD8()`, and `REG_WR8()` for GRC/MMIO register access.
- `MDIO_*` constants are passed to `bnx2x_cl22_read/write()`, `bnx2x_cl45_read/write()`, and related helpers in `bnx2x_link.c` for internal Warpcore and external PHY programming.
- `*_MASK`, `*_SHIFT`, and single-bit constants encode fields for read-modify-write sequences. Several constants are pre-shifted masks, so callers should not assume all values are raw enums.
- `IGU_PF_CONF_*`, `IGU_VF_CONF_*`, `IGU_CMD_*`, `IGU_ADDR_*`, and `IGU_REG_MAPPING_MEMORY_*` are the interrupt-generation-unit ABI used during interrupt enable/disable, VF producer updates, attention signaling, and status-block mapping.
- `AEU_INPUTS_ATTN_BITS_*`, reserved attention bits, and `GENERAL_ATTEN_OFFSET()` provide the attention/parity classification contract used by the driver's interrupt, error, and recovery paths.
- `CDU_VALID_DATA()`, `CDU_CRC8()`, `CDU_RSRVD_VALUE_TYPE_A()`, `CDU_RSRVD_VALUE_TYPE_B()`, and `CDU_RSRVD_INVALIDATE_CONTEXT_VALUE()` define the context validation byte format for CDU-managed connection contexts.
- `calc_crc8(u32 data, u8 crc)` is the only function in this chunk. It splits a 32-bit data word and 8-bit seed into bit arrays, applies the hard-coded CRC-8 XOR network, and returns the recomposed 8-bit result.

High-value constants with visible consumers include `IGU_PF_CONF_FUNC_EN`, `IGU_PF_CONF_MSI_MSIX_EN`, `IGU_PF_CONF_INT_LINE_EN`, `IGU_PF_CONF_ATTN_BIT_EN`, `IGU_PF_CONF_SINGLE_ISR_EN`, `CDU_REGION_NUMBER_UCM_AG`, `CDU_REGION_NUMBER_XCM_AG`, `MDIO_WC_REG_*` Warpcore registers, `MDIO_848xx_CMD_HDLR_*` mailbox registers, `PHY848xx_CMD_*`, `PHY84833_STATUS_*`, `PHY84858_STATUS_*`, `PXP_REG_HST_VF_DISABLED_ERROR_*`, `PBF_REG_DISABLE_NEW_TASK_PROC_Q*`, and the NIG FIFO-empty registers.

## Control Flow And Runtime Use

This header has almost no local control flow; it describes hardware state and access protocols. Runtime flow is distributed through the driver:

1. Initialization and reset paths select a block, calculate a GRC address from these constants, and write enable, credit, mask, parity, or reset values.
2. Interrupt setup in `bnx2x_main.c` reads `IGU_REG_PF_CONFIGURATION`, updates `IGU_PF_CONF_*` bits depending on MSI-X/MSI/INTx mode, acknowledges stale status when needed, and finally sets `IGU_PF_CONF_FUNC_EN`.
3. Interrupt disable clears `IGU_PF_CONF_MSI_MSIX_EN`, `IGU_PF_CONF_INT_LINE_EN`, and `IGU_PF_CONF_ATTN_BIT_EN`; older E1 paths use HC-specific masking while later chips use IGU config directly.
4. Attention/parity handlers classify asserted bits using `AEU_INPUTS_ATTN_BITS_*` and `GENERAL_ATTEN_OFFSET()`-derived masks, then route to block-specific logging, recovery, or fatal paths.
5. Link setup in `bnx2x_link.c` sequences MDIO writes using the MDIO constants. Warpcore AN/KR/KR2/XFI/SFI/SGMII code writes CL73/CL72/BAM, TX FIR/driver, lane control, 64/66, and GP status registers; status reads use GP/link/speed fields to set `link_vars`.
6. External PHY flows use the BCM848xx mailbox definitions by polling status, writing up to five data registers, writing a command, polling for pass/error, and reading result registers.
7. Context initialization in `bnx2x_cmn.c` calls `CDU_RSRVD_VALUE_TYPE_A(HW_CID(...), CDU_REGION_NUMBER_UCM_AG/XCM_AG, ETH_CONNECTION_TYPE)` to stamp USTORM/XSTORM contexts with validation bytes derived by `calc_crc8()`.
8. SR-IOV paths use IGU command ranges such as `IGU_CMD_E2_PROD_UPD_BASE + igu_sb_id` to build VF producer-update addresses.
9. Self-test/idle-check tables reference the idle-check register constants to verify PXP, PBF, QM, and NIG quiescence or error state.

## State And Persistence Behavior

The header itself is stateless. The state it names is persistent hardware state across many calls and sometimes across function-level reset boundaries until explicitly cleared or reinitialized.

State-sensitive areas include:

- Timer/SDM/SEM/CM registers hold interrupt, parity, queue, credit, context, arbitration, and FIFO state. Some status registers are read-clear (`RC`), so reads can acknowledge or destroy diagnostic evidence.
- Interface-enable and credit registers gate traffic between internal blocks. Wrong values can stall command, completion, timer, storm, or queue-manager traffic.
- SEM free/sleeping-thread lists, FIC/PAS disables, PRAM, fast memory, passive-buffer memory, and interrupt tables represent microcode engine runtime state and should not be treated as ordinary scratch registers.
- MAC registers hold link-facing state such as TX/RX enable, reset, max frame size, source MAC for pause/PFC frames, EEE behavior, pause/PFC enables, and link-fault status.
- MCP/NVM lock and command bits coordinate access to firmware/NVRAM resources. The hardware-lock constants define shared ownership between driver, management firmware, and other functions.
- PCIe/PXPCS status bits are often write-clear or read-only diagnostics. Misclassification can hide fatal PCIe conditions or cause noisy attention handling.
- MDIO/PHY registers persist link mode, advertised capabilities, lane polarity/swap, equalization, firmware mode, EEE, SFP two-wire access state, and PHY mailbox status.
- IGU configuration controls whether a PF/VF can generate interrupts, whether MSI-X/MSI/INTx is active, which parent PF a VF maps to, and how mapping-memory entries encode vector/FID ownership.
- CDU validation bytes persist in connection contexts and are consumed by hardware context validation.

## Dependencies And Integration Points

- `bnx2x_main.c`: consumes IGU PF configuration, AEU attention bits, XCM masks, BAR/IGU command offsets, reset/MISC constants, and block bases during load/unload, interrupt mode transitions, parity handling, and recovery.
- `bnx2x_link.c`: the dominant consumer of MDIO/PHY, MAC, NIG/PBF, MCP/NVM, GPIO/SPIO, and Warpcore constants. It programs autonegotiation, forced speeds, PHY firmware modes, EEE, SFP/two-wire access, lane reset/polarity, and LED/media behavior.
- `bnx2x_cmn.c`: uses CDU region and CRC macros in `bnx2x_set_ctx_validation()` to stamp connection contexts.
- `bnx2x_sriov.c`: uses IGU command producer-update ranges for VF status-block producer writes.
- `bnx2x_self_test.c`: uses idle-check registers to define hardware health/quiescence probes.
- `bnx2x.h` and `bnx2x_init.h`: compose attention/parity masks from `AEU_INPUTS_ATTN_BITS_*` and `GENERAL_ATTEN_OFFSET()` definitions.
- Firmware and hardware specifications: many comments mention generated design names and internal blocks, making these constants a contract with device RTL/firmware rather than normal driver-local policy.

## Risks And Edge Cases

- Address or bit drift is high impact. A wrong constant can write to the wrong hardware block, corrupt link setup, mask a parity event, break MSI-X/MSI/INTx routing, or stall an internal queue.
- Several registers are read-clear or write-clear. Diagnostic code must not casually read `*_STS_CLR`, length-mismatch, parity, PCIe error, or mailbox status registers unless it intends to acknowledge them.
- Constants mix raw values, shifted masks, and encoded values. For example, many MDIO/PCI/IGU fields are already shifted; double-shifting or using a mask as a value can corrupt neighboring bits.
- Link programming is tightly sequenced. Warpcore setup frequently changes AER lane selection, disables AN, writes global and lane-specific registers, restores AER, resets lanes, and then restarts AN. Reordering register writes can leave a lane stuck or report false link.
- Shared-resource locks matter. NVM, MDIO, GPIO/SPIO, reset, and DCBX/admin resources are coordinated through hardware-lock IDs; bypassing these risks races with firmware or another PF.
- `CDU_RSRVD_VALUE_TYPE_B(_crc, _type)` appears malformed in this chunk because it references `_cid` and `_region` inside the body despite not accepting those parameters. It appears unused in the local `bnx2x` tree, but using it as written would not compile.
- `calc_crc8()` comment says it splits data into 31 bits, but the loop processes 32 bits. The implementation, not the comment, is what CDU validation depends on.
- Some PHY definitions are vendor/model-specific. Applying BCM84833/84858 mailbox statuses, BCM84823 media straps, 54618SE GPHY shadows, or Warpcore registers to the wrong PHY path can hang polling loops or misconfigure media.
- Duplicate BAR constants appear in this chunk. They match earlier definitions here, but future edits should avoid creating divergent duplicate values.
- Idle-check constants are hardware-generation sensitive. Some NIG/PBF/QM empty signals or queue IDs may only be valid on specific chip revisions or traffic modes.

## Test And Validation Signals

- Build signal: `bnx2x` must compile with all consumers of these symbols. Any changed macro name, invalid macro body, or missing address constant will usually fail at compile time.
- Interrupt-mode smoke: load/unload the driver with MSI-X, MSI, and INTx where supported; verify `IGU_REG_PF_CONFIGURATION` updates do not leave interrupts disabled, duplicated, or stuck.
- Link bring-up: validate autoneg and forced modes across supported media, especially KR/KR2/XFI/SFI/SGMII paths that use `MDIO_WC_REG_*` sequencing. Useful observations are link-up, negotiated speed/duplex, pause/FEC/EEE negotiation, and no repeated link recovery.
- PHY mailbox: for BCM84833/84858, exercise pair-swap and EEE mailbox commands and verify pass/error/timeout handling around `MDIO_848xx_CMD_HDLR_*` and `PHY848xx_*` statuses.
- Context validation: exercise L2 connection setup and teardown so `bnx2x_set_ctx_validation()` stamps USTORM/XSTORM contexts; hardware should accept contexts without CDU validation faults.
- Attention/parity handling: inject or observe AEU attention/parity conditions if supported by test hardware; verify the asserted bits map to the expected block names and recovery behavior.
- SR-IOV: verify VF producer updates, interrupt delivery, and parent PF/FID mapping with VFs enabled.
- Idle check: run the driver's self-test/idle-check path after quiescing traffic and confirm PXP/PBF/QM/NIG checks using this chunk's registers pass or produce meaningful failures.

## Chunk Notes For Merge Lane

This chunk is the tail of `bnx2x_reg.h` and includes both generated-style hardware register definitions and the file-closing `calc_crc8()` helper. The final per-file report should treat `bnx2x_reg.h` as a hardware register contract consumed throughout the driver, not as standalone driver logic. Earlier chunks are needed for the rest of the block register map; this chunk contributes the key link/PHY, interrupt/attention, IGU/CDU, idle-check, and CRC-validation portions.
