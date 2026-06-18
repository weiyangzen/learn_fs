<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h

Purpose: Defines SN0 hub Memory/Directory register offsets, memory-bank configuration fields, directory/protection entry formats, page migration controls, error register formats, LED helpers, and performance counter formats.

Important APIs/types/functions: `MD_*` register offsets, memory size constants and `MD_SIZE_BYTES/MBYTES`, `MMC_*` memory config fields, refresh/DIMM/MOQ/MLAN fields, directory states `MD_DIR_*`, premium/standard directory masks, protection/migration fields, LED macros `CPU_LED_ADDR`, `SET_CPU_LEDS`, migration threshold/candidate macros, error unions `md_dir_error_t`, `md_mem_error_t`, `md_proto_error_t`, directory entry unions, `dir_mem_entry_t`, and MD perf counter unions.

Control flow: Memory setup programs memory config/refresh/DIMM registers, directory code initializes directory/protection entries, NUMA migration code configures thresholds and reads candidates, diagnostics read/clear MD error registers, and LED/debug code writes hub LED registers.

State and persistence: State is the hub MD register block, memory bank sizing, directory/protection memory, migration counters/candidates, ECC/protocol/misc error latches, MLAN/NIC controls, and performance counters.

Dependencies and integration points: Used by SN memory initialization, NUMA/page-migration code, error handlers, and diagnostics. Relies on `REMOTE_HUB_L/S`, `get_nasid`, `get_slice`, and platform private data through includers.

Risks: Directory and protection bitfields are hardware ABI. Incorrect migration threshold or directory writes can affect coherency. The header includes legacy typo/duplicate artifacts (`md_dir_error_t` duplicated close, `MMCE_lONG_PACK_SHFT`) that should be handled carefully.

Test signals: SN memory discovery, ECC/protocol error injection, page migration enable/disable tests, LED diagnostics, and build coverage for premium/standard directory modes are relevant.

Source read size: 789 lines, 26673 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h -->
