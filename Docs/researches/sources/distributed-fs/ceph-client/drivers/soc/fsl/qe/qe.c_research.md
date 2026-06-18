# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe.c

## Purpose
Core QUICC Engine management implementation. It discovers and maps QE registers, resets the engine, initializes SNUMs and SDMA, issues QE commands, configures BRG clocks, parses clock names, uploads QE firmware/microcode, and exposes firmware and hardware-capacity information.

## Important APIs, types, and functions
Exports include `qe_immr`, `cmxgcr_lock`, `qe_reset`, `qe_issue_cmd`, `qe_get_brg_clk`, `qe_setbrg`, `qe_clock_source`, `qe_get_snum`, `qe_put_snum`, `qe_upload_firmware`, `qe_get_firmware_info`, `qe_get_num_of_risc`, and `qe_get_num_of_snums`. Private helpers include `qe_get_device_node`, `get_qe_base`, `qe_snums_init`, `qe_sdma_init`, `qe_upload_microcode`, and the PPC resume hook.

## Control flow and state behavior
`qe_init` runs at `subsys_initcall`, finds `"fsl,qe"`, and calls `qe_reset`. Reset maps `qe_immr` if necessary, initializes SNUM tables, issues a reset command, initializes MURAM, and configures SDMA temporary buffers. `qe_issue_cmd` serializes command register access with `qe_lock`, formats command fields according to reset, page assignment, RISC assignment, USB, or normal command semantics, and polls for `QE_CR_FLG` to clear.

SNUM allocation uses a bitmap protected by `qe_lock`; the SNUM table comes from `fsl,qe-snums` or legacy static arrays selected by `fsl,qe-num-snums`. Firmware upload validates magic, version, microcode count, length, and CRC, optionally splits I-RAM, uploads each microcode blob with auto-increment writes, programs traps, enables trap registers, and snapshots firmware info for later query. `qe_get_firmware_info` can also synthesize state from a firmware child node provided by firmware/bootloader.

## Dependencies and integration points
Depends on device tree QE bindings, `qe_common.c` MURAM APIs, CRC32, big-endian MMIO, PPC errata helpers, suspend support, and public QE headers. Downstream UCC, TDM, serial, Ethernet, USB, and QMC drivers consume its exported command, clock, SNUM, and firmware APIs.

## Risks and test signals
`qe_issue_cmd` returns `ret == 0`, so success is `1` and timeout is `0`, which is unusual for kernel APIs and can confuse callers. Firmware upload trusts structure packing and big-endian offsets and should be fuzzed through invalid length/count/CRC cases. Test signals include successful subsystem init, SNUM exhaustion/release behavior, BRG programming for errata-affected SoCs, firmware CRC rejection, and resume reset behavior on PPC 85xx.
