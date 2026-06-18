# subset-b-004991 research

Grouped research report for the requested source-tree-aligned files. Each section is delimited for reconciliation into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.c

Purpose: NVMEM layout driver for U-Boot environment images. It validates the environment CRC, interprets single, redundant, and Broadcom image headers, and registers each `name=value` entry as an NVMEM cell.

Important APIs/types/functions: `u_boot_env_parse()` is exported for providers; `u_boot_env_add_cells()` wires the parser into `struct nvmem_layout`; `u_boot_env_parse_cells()` mutates the read buffer into C strings and calls `nvmem_add_one_cell()`; `u_boot_env_read_post_process_ethaddr()` converts an `ethaddr` string to six bytes and applies index-based MAC increments. Image structs describe single CRC-only, redundant CRC+mark, and Broadcom magic/len/CRC layouts.

Control flow: probe installs `layout->add_cells` and registers the layout. Parsing chooses offsets from the matched format, reads either `env-size` or the full NVMEM size, computes little-endian CRC32 over the payload, NUL-terminates the buffer, then walks NUL-separated variables until a missing `=` or empty variable stops parsing.

State/persistence: no persistent state beyond dynamically registered NVMEM cells. It allocates a temporary full-image buffer and uses devm allocations for cell names; the underlying provider owns the actual nonvolatile storage.

Dependencies/integration: depends on the NVMEM provider/layout APIs, OF compatibles `u-boot,env`, redundant variants, and `brcm,env`; optionally links cells to child OF nodes by variable name. The top-level MTD-backed provider in `drivers/nvmem/u-boot-env.c` calls the exported parser.

Risks: CRC endianness is read through a cast rather than `le32_to_cpup()`, so this assumes little-endian interpretation consistent with the target build. Parsing writes NULs into the temporary buffer, so callers must provide writable data. Malformed environments stop cell discovery silently after a variable without `=`.

Test signals: exercise valid and invalid CRC images for all three formats; verify `env-size` truncation, NVMEM read short-read handling, `ethaddr` post-processing with indexed aliases, and OF child-cell association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.h -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.h

Purpose: Small shared header for U-Boot environment layout parsing.

Important APIs/types/functions: defines `enum u_boot_env_format` with `U_BOOT_FORMAT_SINGLE`, `U_BOOT_FORMAT_REDUNDANT`, and `U_BOOT_FORMAT_BROADCOM`; declares `u_boot_env_parse(struct device *, struct nvmem_device *, enum u_boot_env_format)`.

Control flow: there is no runtime flow; it is a compile-time contract between the layout parser and providers that need to parse the same image formats.

State/persistence: no state. The enum values are used as OF match data cast through pointer-sized fields.

Dependencies/integration: included by the layout driver and MTD-backed `u-boot-env` provider. It assumes the including translation unit has visible declarations for `struct device` and `struct nvmem_device`.

Risks: enum ordering is part of the local match-data convention, so changing it would alter existing compatible handling unless all users are updated together.

Test signals: compile coverage for both users and format-specific parser tests cover this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_eeprom.c

Purpose: NXP LPC18xx/LPC43xx EEPROM NVMEM provider with readable and writable word access.

Important APIs/types/functions: `struct lpc18xx_eeprom_dev` stores clock, register and memory mappings, access widths, and size. `lpc18xx_eeprom_read()` and `lpc18xx_eeprom_gather_write()` implement NVMEM callbacks; `lpc18xx_eeprom_busywait_until_prog()` polls `END_OF_PROG`; probe maps named `reg` and `mem` resources, configures clock divider/autoprogramming, powers down the EEPROM, and registers `lpc18xx_nvmem_config`.

Control flow: probe enables the EEPROM clock, asserts reset, programs the divider for roughly 1.5 MHz EEPROM operation, enables word autoprogramming, powers the block down, then exposes 4-byte stride/word NVMEM. Reads and writes power up, wait 100 us, transfer 32-bit words, and power down; writes wait for completion after each word.

State/persistence: EEPROM contents persist in hardware. Driver state is devm-managed except the prepared/enabled clock, which is disabled in remove or on probe failure. The last page is reserved for initialization data and rejected for writes.

Dependencies/integration: platform driver for `nxp,lpc1857-eeprom`; uses named memory resources, reset controller, clock framework, MMIO, and NVMEM provider core.

Risks: callbacks assume 4-byte aligned accesses supplied by NVMEM stride/word rules. Error paths during write can leave the EEPROM powered if failure occurs before the final power-down. The global static `nvmem_config` is modified at probe, which is typical for single-instance platform drivers but unsafe for unexpected multiple instances.

Test signals: validate read/write with aligned 4-byte operations, timeout behavior when `END_OF_PROG` never arrives, rejection of writes into the protected final page, and clock/reset cleanup on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_otp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_otp.c

Purpose: Read-only NVMEM provider for LPC18xx/43xx OTP banks.

Important APIs/types/functions: `struct lpc18xx_otp` holds the MMIO base. `lpc18xx_otp_read()` copies 32-bit OTP words. `lpc18xx_otp_nvmem_config` declares read-only, 4-byte stride/word access and fixed 64-byte size.

Control flow: probe allocates state, maps resource 0, fills config size/device/private fields, and registers the NVMEM device. Reads convert byte offset and length to word index/count and perform `readl()` across the requested words.

State/persistence: OTP data is hardware-programmed and read-only through this driver. No runtime persistence beyond the devm-managed mapping and registered NVMEM device.

Dependencies/integration: platform driver matched by `nxp,lpc1850-otp`; integrates with NVMEM fixed cells and consumers for part IDs, keys, USB IDs, or general-purpose OTP words.

Risks: the boundary check compares word count against a byte-sized constant after `index` conversion, so it is permissive rather than a precise byte bound; NVMEM core size normally limits callers. The TODO notes write support through boot ROM is absent.

Test signals: read all four banks, check 4-byte alignment behavior, and verify invalid/out-of-range requests are contained by NVMEM core sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/max77759-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/max77759-nvmem.c

Purpose: EEPROM-like NVMEM provider for Maxim MAX77759, using the parent MFD's MAXQ command transport.

Important APIs/types/functions: `struct max77759_nvmem` links the platform child to the parent `struct max77759`. `max77759_nvmem_reg_read()` sends `MAX77759_MAXQ_OPCODE_USER_SPACE_READ`; `max77759_nvmem_reg_write()` sends `MAX77759_MAXQ_OPCODE_USER_SPACE_WRITE`; probe registers an EEPROM-type NVMEM device with byte stride and `ignore_wp = true`.

Control flow: NVMEM reads/writes build MAXQ command and response buffers with a three-byte opcode/offset/length header. The response must echo the header for reads and the whole command for writes; otherwise the callback reports `-EIO`.

State/persistence: data persists inside MAX77759 user-space NVMEM. Driver state is per-device and devm-managed; no cache is kept.

Dependencies/integration: depends on `linux/mfd/max77759.h` and the parent MFD drvdata/command path; matches OF `maxim,max77759-nvmem` and platform id `max77759-nvmem`.

Risks: maximum readable/writable size is bounded by command payload length, and callers rely on NVMEM core to enforce `.size`. Protocol echo mismatches are warned but not retried. Write protection is explicitly ignored at NVMEM config level because access control is delegated to the transport/device.

Test signals: mock MAXQ responses for successful read/write, transport errors, header mismatch, oversized NVMEM requests, and parent drvdata absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/max77759-nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/meson-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/meson-efuse.c

Purpose: Amlogic Meson GX eFuse NVMEM provider mediated through secure monitor firmware.

Important APIs/types/functions: `meson_efuse_read()` and `meson_efuse_write()` call `meson_sm_call_read()`/`meson_sm_call_write()` with `SM_EFUSE_READ` and `SM_EFUSE_WRITE`. Probe resolves the `secure-monitor` phandle, obtains `struct meson_sm_firmware`, enables the eFuse gate clock, asks firmware for `SM_EFUSE_USER_MAX`, and registers byte-granular NVMEM.

Control flow: probe defers until secure monitor firmware is available, then computes the size from firmware and exposes read/write callbacks. Runtime NVMEM operations are direct firmware calls that return 0 on nonnegative secure monitor result.

State/persistence: eFuse contents persist in silicon; the driver stores only firmware pointer/config. Writes are permanent if firmware allows them.

Dependencies/integration: platform driver for `amlogic,meson-gxbb-efuse`; depends on Meson secure monitor firmware and a clock gate.

Risks: write availability is exposed to NVMEM consumers, so policy is entirely dependent on firmware and NVMEM permissions. Probe fails if firmware cannot return the user size. Secure monitor call argument semantics are opaque to this driver.

Test signals: secure monitor present/deferred/failing paths, size query failure, read/write firmware errors, and fixed-cell reads through legacy OF cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/meson-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/meson-mx-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/meson-mx-efuse.c

Purpose: Read-only NVMEM provider for older Amlogic Meson6/Meson8/Meson8b eFuse controllers.

Important APIs/types/functions: `struct meson_mx_efuse_platform_data` supplies name and word size; `meson_mx_efuse_hw_enable()`/`hw_disable()` gate clock and power; `meson_mx_efuse_read_addr()` programs byte address, starts auto-read, polls busy, and reads data; `meson_mx_efuse_read()` loops across requested words.

Control flow: probe chooses compatible-specific word size, maps MMIO, gets the `core` clock, and registers a 512-byte read-only OTP NVMEM. Reads power the block, enable auto-read, iterate address conversions, copy partial final words, disable auto-read, and power down.

State/persistence: hardware eFuse is persistent and read-only. Driver state holds base, clock, and embedded `nvmem_config`.

Dependencies/integration: OF compatibles `amlogic,meson6-efuse`, `amlogic,meson8-efuse`, and `amlogic,meson8b-efuse`; uses MMIO, clock framework, polling helpers, and legacy fixed OF cells.

Risks: timeouts return after logging the failing address. The read path must always balance power/clock disable; current flow does so after loop exit. Static size is fixed to 512 bytes regardless of SoC-specific exposed data.

Test signals: compatible-specific word-size behavior, unaligned/partial reads, timeout path from `AUTO_RD_BUSY`, clock enable failures, and fixed-cell consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/meson-mx-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/microchip-otpc.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/microchip-otpc.c

Purpose: Read-only NVMEM provider for Microchip SAMA7G5 OTPC packetized OTP memory.

Important APIs/types/functions: `struct mchp_otpc` owns MMIO base, device, packet list, and packet count. `struct mchp_otpc_packet` maps logical packet IDs to hardware word offsets. `mchp_otpc_init_packets_list()` scans headers to build the packet table; `mchp_otpc_read()` translates NVMEM offsets to packet IDs and reads headers/payloads through `mchp_otpc_prepare_read()`.

Control flow: probe maps the controller, scans packets until a zero payload size or the maximum memory size is reached, sets the NVMEM size to accumulated packet bytes, and registers read-only 4-byte stride access. Runtime reads divide the NVMEM offset by four to identify a packet, trigger controller reads for each packet, copy header then payload words, and continue until the requested byte count is filled.

State/persistence: OTP contents persist in hardware. The packet list is devm-allocated at probe and forms the stable logical index for NVMEM consumers.

Dependencies/integration: platform driver for `microchip,sama7g5-otpc`; uses bitfield helpers, MMIO polling, NVMEM provider, and legacy fixed OF cells.

Risks: the NVMEM address space is packet-ID oriented, not a raw physical byte map, so consumers must understand the packet layout. Payload loop uses the header's size field and must trust hardware to avoid malformed packet sequences; probe bounds scanning by `MCHP_OTPC_SIZE`.

Test signals: packet-list construction from multiple payload sizes, invalid packet IDs returning `-EINVAL`, controller read timeout, and cell reads that include header and payload words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/microchip-otpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/mtk-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/mtk-efuse.c

Purpose: MediaTek eFuse NVMEM provider with optional post-processing for GPU speed-bin cells.

Important APIs/types/functions: `mtk_reg_read()` byte-copies MMIO eFuse data. `mtk_efuse_fixup_dt_cell_info()` attaches `mtk_efuse_gpu_speedbin_pp()` to small `gpu-speedbin` cells on SoCs needing conversion from numeric bin to bitmask. Probe registers NVMEM and creates a child `mtk-socinfo` platform device.

Control flow: probe maps the eFuse resource, chooses compatible match data, fills a byte-granular read-only NVMEM config sized from the resource, optionally installs the fixup callback, registers NVMEM, then registers `mtk-socinfo`. Remove unregisters that child device.

State/persistence: eFuse data is persistent hardware state. The driver persists only the MMIO base and optional child platform device pointer.

Dependencies/integration: OF compatibles include `mediatek,mt8173-efuse`, `mediatek,mt8186-efuse`, and generic `mediatek,efuse`; integrates with NVMEM fixed cells and MediaTek SoC information driver.

Risks: `pdata` is assumed non-NULL from match data. The prefix comparison for `gpu-speedbin` uses the shorter of actual and expected lengths, so very short names that prefix-match could be post-processed. SoC info registration failure is informational, not fatal.

Test signals: raw byte reads, MT8186 speed-bin cell conversion, child device registration/unregistration, and missing match-data probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/mtk-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/mxs-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/mxs-ocotp.c

Purpose: Freescale MXS/i.MX23/i.MX28 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `struct mxs_ocotp` holds clock, MMIO base, and NVMEM device. `mxs_ocotp_wait()` polls busy/error bits. `mxs_ocotp_read()` opens OCOTP banks for read, returns zeros for non-data or unaligned register offsets, and copies data words. Match data supplies SoC-specific size.

Control flow: probe maps the controller, obtains and prepares the clock, registers cleanup action to unprepare it, and exposes 16-byte stride/4-byte word reads. Each read enables the clock, clears stale error, waits idle, opens banks, delays, waits again, reads requested words, closes banks, and disables the clock.

State/persistence: OTP state is persistent in hardware and read-only. Runtime state is limited to clock preparation and MMIO mapping.

Dependencies/integration: compatibles `fsl,imx23-ocotp` and `fsl,imx28-ocotp`; uses STMP set/clear register offsets, clock framework, and NVMEM provider.

Risks: polling is CPU-relax busy-wait with a fixed iteration count. The driver intentionally masks non-data regions with zeros, which can hide incorrect cell offsets. Author module string has a missing closing parenthesis but no runtime effect.

Test signals: clock enable failure, busy/error timeout, reads from data and non-data offsets, and SoC size selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/mxs-ocotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/nintendo-otp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/nintendo-otp.c

Purpose: Read-only, root-only NVMEM provider for Nintendo Wii and Wii U OTP banks.

Important APIs/types/functions: `struct nintendo_otp_devtype_data` supplies NVMEM name and bank count for Hollywood and Latte devices. `nintendo_otp_reg_read()` issues big-endian OTP read commands and reads big-endian data words.

Control flow: probe matches compatible data, maps the register window, fills a 4-byte stride read-only/root-only NVMEM config sized by bank count, and registers it. Reads compute bank/address from the byte offset, write `OTP_READ | bank | addr` to `HW_OTPCMD`, then read `HW_OTPDATA`.

State/persistence: OTP contents are per-console keys/signatures and persist in hardware. Driver state is only the MMIO mapping.

Dependencies/integration: OF compatibles `nintendo,hollywood-otp` and `nintendo,latte-otp`; relies on big-endian MMIO accessors and NVMEM permissions to restrict root access.

Risks: sensitive key material is exposed through NVMEM to root. No explicit command-completion polling is present, so hardware is assumed to provide data synchronously after command write.

Test signals: bank-size mapping for Wii versus Wii U, big-endian read command formation, root-only sysfs visibility, and multiword reads crossing bank boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/nintendo-otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qcom-spmi-sdam.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/qcom-spmi-sdam.c

Purpose: Qualcomm SPMI SDAM NVMEM provider for small PMIC scratch/data memory.

Important APIs/types/functions: `struct sdam_chip` stores parent regmap, base, size, and embedded config. `sdam_is_valid()` allows memory window accesses and one-byte PBS trigger registers. `sdam_is_ro()` prevents writes over read-only ID/version/size registers. `sdam_read()`/`sdam_write()` use regmap bulk operations.

Control flow: probe obtains the parent's regmap, reads the child `reg` base from OF, reads `SDAM_SIZE`, computes bytes as `val * 32`, and registers byte-granular read/write NVMEM. Runtime access validates range and write permissions before issuing regmap operations.

State/persistence: SDAM data may persist according to PMIC behavior; the driver has no cache. PBS trigger registers are exposed as special one-byte valid offsets.

Dependencies/integration: platform driver for `qcom,spmi-sdam`; depends on parent SPMI/regmap device and legacy fixed OF NVMEM cells.

Risks: NVMEM config size is set to SDAM memory size only, while valid access also permits trigger offsets outside that range; generic NVMEM bounds may prevent external access to those trigger registers unless cells account for it. Writes to partially overlapping RO registers are rejected.

Test signals: invalid range rejection, RO write rejection, SDAM_SIZE-derived sizing, regmap read/write errors, and PBS trigger single-byte access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qcom-spmi-sdam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qfprom.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/qfprom.c

Purpose: Qualcomm QFPROM NVMEM provider for corrected/raw fuse reads and optional permanent fuse programming.

Important APIs/types/functions: `struct qfprom_priv` stores corrected, raw, config, and security MMIO regions plus clock/regulator/power data. `qfprom_reg_read()` reads corrected data by default or raw data under module parameter `read_raw_data`. `qfprom_enable_fuse_blowing()` and `qfprom_disable_fuse_blowing()` sequence clock rate, regulator voltage, runtime PM, genpd performance, timer, and accel values. `qfprom_reg_write()` performs aligned word writes to raw fuses. `qfprom_fixup_dt_cell_info()` aligns NVMEM cells to 32-bit read granularity.

Control flow: probe always maps corrected space and registers read access. If raw/config/security resources exist, it maps them, reads QFPROM version, selects known SoC programming constants, gets regulator and optional clock, and enables writes only when all required programming data is available. Read path loops 32-bit words. Write path validates word alignment, enables fuse-blowing conditions, waits for ready, writes each word, waits for ready again, then restores all touched hardware state.

State/persistence: fuses are permanent. Runtime state includes MMIO mappings and supplies; `read_raw_data` is mutable module state affecting all instances. Keepout tables hide SoC-specific unsafe ranges from NVMEM access.

Dependencies/integration: OF compatibles `qcom,qfprom`, `qcom,sc7180-qfprom`, and `qcom,sc7280-qfprom`; depends on regulator, clock, runtime PM, power domains, NVMEM keepouts, and fixed OF cells.

Risks: write operations are irreversible and rely on exact clock/voltage/timer sequencing. Writes are silently unavailable on unsupported QFPROM versions or absent clock/soc data. Raw reads through a module parameter may expose uncorrected or sensitive data. The 32-bit cell fixup changes offsets/bit offsets, so cell definitions must be validated carefully.

Test signals: corrected versus raw read mode, keepout enforcement, unsupported write setup, alignment errors, regulator/clock/genpd failure unwinding, fuse-blow timeout, and DT cell fixup for unaligned cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qfprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qnap-mcu-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/qnap-mcu-eeprom.c

Purpose: Read-only EEPROM NVMEM provider behind a QNAP MCU command protocol.

Important APIs/types/functions: `qnap_mcu_eeprom_read_block()` sends command `{0xf7, 0xa1, offset, bytes}` through `qnap_mcu_exec()` and validates echoed command bytes. `qnap_mcu_eeprom_read()` chunks arbitrary reads into 32-byte blocks. Probe registers a 256-byte EEPROM NVMEM device using the parent MCU drvdata.

Control flow: probe gets `struct qnap_mcu` from the parent, fills byte-granular read-only NVMEM config, and registers. Reads loop until requested bytes are consumed, issuing at most 32 bytes per MCU transaction.

State/persistence: EEPROM data persists behind the MCU. The driver allocates a temporary reply buffer per block read and keeps no cache.

Dependencies/integration: depends on `linux/mfd/qnap-mcu.h`, parent platform/MFD device, and NVMEM provider core; no OF match table because the child is platform-created by the MCU driver.

Risks: offset is encoded in one command byte, matching the fixed 256-byte size. Protocol echo mismatch returns `-EIO`; no retries are attempted. Block size was determined empirically, so larger transfers may be unreliable.

Test signals: zero-length reads, multi-block reads, echo mismatch, MCU transport errors, and NVMEM size boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qnap-mcu-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qoriq-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/qoriq-efuse.c

Purpose: Read-only, root-only NVMEM provider for NXP QorIQ Security Fuse Processor data.

Important APIs/types/functions: `struct qoriq_efuse_priv` holds MMIO base. `qoriq_efuse_read()` uses `__ioread32_copy()` for aligned 32-bit reads. Probe maps the resource and registers a 4-byte stride NVMEM device named `qoriq_efuse_read`.

Control flow: probe allocates state, maps resource 0, sizes config from the resource, and registers NVMEM. Runtime reads copy `bytes / 4` words from base plus offset.

State/persistence: eFuse data persists in hardware and is read-only through this driver. No runtime cache.

Dependencies/integration: platform driver for `fsl,t1023-sfp`; uses MMIO and NVMEM provider APIs.

Risks: trailing non-word bytes are intentionally ignored, relying on `.stride = 4` to prevent such requests. Root-only is set because SFP contents may include security-sensitive data.

Test signals: aligned 32-bit reads, root-only permissions, resource-size config, and attempted unaligned access through NVMEM core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/qoriq-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rave-sp-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/rave-sp-eeprom.c

Purpose: Read/write EEPROM NVMEM provider for ZII RAVE SP devices over the parent service processor protocol.

Important APIs/types/functions: `struct rave_sp_eeprom` stores parent SP pointer, mutex, EEPROM address, header size, and device. `rave_sp_eeprom_io()` formats low-level read/write page commands and validates response type/success. `rave_sp_eeprom_page_access()` handles single-page reads/writes, including read-modify-write for partial pages. `rave_sp_eeprom_access()` splits arbitrary NVMEM access at 32-byte page boundaries.

Control flow: probe parses `reg = <address size>`, rejects sizes too large for 16-bit page addressing, selects 4- or 5-byte command header depending on size > 8 KiB, initializes mutex, and registers byte-granular read/write NVMEM. Runtime access is serialized and chunked so no low-level operation crosses a page.

State/persistence: EEPROM contents persist on the RAVE SP-managed device. The driver keeps only protocol parameters and no data cache.

Dependencies/integration: OF compatible `zii,rave-sp-eeprom`; depends on parent `rave_sp_exec()`, NVMEM provider, OF `zii,eeprom-name`, and legacy fixed cells.

Risks: partial writes require a prior read; if read succeeds but write fails, data is unchanged but caller only sees protocol failure. All accesses serialize through one mutex, which is safe but limits throughput. Protocol response validation is minimal: type and success flag.

Test signals: small versus big header command formatting, page-boundary chunking, partial write read-modify-write, response type mismatch `-EPROTO`, failed success flag `-EIO`, and maximum-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rave-sp-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rcar-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/rcar-efuse.c

Purpose: Renesas R-Car E-FUSE/OTP read-only NVMEM provider with SoC-specific accessible windows.

Important APIs/types/functions: `struct rcar_fuse_data` selects resource bank and valid `[start,end)` window. `rcar_fuse_reg_read()` runtime-resumes the device, copies 32-bit words, and runtime-suspends. Probe constructs two keepout regions around the valid window.

Control flow: probe enables runtime PM, allocates state, maps the selected memory resource bank, computes keepouts from match data and resource size, and registers root-only OTP NVMEM. Reads are 4-byte stride copies under runtime PM.

State/persistence: fuse contents persist in hardware; driver state holds keepout table, base, and device pointer.

Dependencies/integration: compatibles for R-Car V3U, S4, V4H, and V4M variants; depends on runtime PM, NVMEM keepouts, and MMIO.

Risks: match data is assumed present. Keepout correctness is critical because the mapped resource may contain non-fuse registers around the valid region. Runtime PM errors propagate to reads.

Test signals: per-compatible bank/window selection, keepout enforcement, runtime PM failure path, and root-only read permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rcar-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/rmem.c

Purpose: NVMEM provider backed by reserved memory, with optional Mobileye EyeQ5 bootloader-config checksum validation.

Important APIs/types/functions: `struct rmem` stores device, NVMEM, and `struct reserved_mem`. `rmem_read()` maps the reserved region with `memremap()`, copies the requested bytes, and unmaps immediately. `rmem_eyeq5_checksum()` validates magic, size, and CRC32 over the reserved-memory payload before registration.

Control flow: probe looks up reserved memory by the device node, fills NVMEM config with size and read callback, optionally runs compatible-specific checksum, then registers. Reads bounds-check against reserved memory size and map only during the read.

State/persistence: the backing region is reserved RAM populated by firmware/bootloader; it persists across kernel runtime but not necessarily across power cycles. Driver has no write path and no cache.

Dependencies/integration: compatibles `nvmem-rmem` and `mobileye,eyeq5-bootloader-config`; depends on reserved-memory OF binding, memremap, CRC32, and NVMEM provider.

Risks: repeated reads remap the entire reserved region, which is simple but inefficient for large/frequent reads. Checksum validation allocates `header.size`; size is bounded by reserved memory before allocation. The memory is not made read-only, so other kernel code could still corrupt it if mapped elsewhere.

Test signals: missing reserved memory, read bounds failure, EyeQ5 bad magic/size/CRC, successful checksum, and NVMEM reads after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-efuse.c

Purpose: Read-only OTP NVMEM provider for older Rockchip eFuse controllers.

Important APIs/types/functions: `struct rockchip_efuse_chip` holds device, base, and `pclk_efuse`. `rockchip_rk3288_efuse_read()`, `rockchip_rk3328_efuse_read()`, and `rockchip_rk3399_efuse_read()` implement SoC-family-specific register sequences. Match data is a function pointer used as `econfig.reg_read`.

Control flow: probe resolves match-data read function, maps MMIO, gets clock, chooses size from `rockchip,efuse-size` or resource size, and registers byte-granular read-only NVMEM. Runtime reads enable the clock, execute the family-specific address/strobe/auto-read flow, copy aligned temporary data as needed, put hardware in standby, and disable the clock.

State/persistence: eFuse data is persistent and read-only. Driver state is MMIO/clock only; no cache.

Dependencies/integration: supports deprecated generic and SoC-specific compatibles from RK3066A through RK3399; uses clock framework, MMIO, OF property sizing, and legacy fixed cells.

Risks: RK3328 offsets are shifted by the secure-region size, exposing only non-secure bytes. Static global `econfig` is mutated per probe. Polling/interrupt status handling differs by SoC and needs hardware-specific coverage.

Test signals: all compatible function selections, RK3328 secure offset translation, partial reads over 4-byte words, missing `rockchip,efuse-size`, and clock enable failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-otp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-otp.c

Purpose: Read-only NVMEM provider for newer Rockchip OTP controllers with reset, bulk clocks, optional ECC, and variant-specific word sizes.

Important APIs/types/functions: `struct rockchip_data` defines size, read offset, word size, clock names, and low-level read callback. `rockchip_otp_read()` is the NVMEM callback and adapts byte requests to variant word reads. `px30_otp_read()`, `rk3568_otp_read()`, and `rk3588_otp_read()` implement controller generations. Helpers reset the OTP PHY, poll status, and enable/disable ECC through SBPI.

Control flow: probe selects match data, maps MMIO, allocates clock bulk array, gets clocks and reset controls, fills static NVMEM config, and registers. Reads enable all clocks, add any variant read offset, allocate temporary word buffers for multi-byte word sizes, call the low-level reader, copy requested bytes, and disable clocks.

State/persistence: OTP contents persist in hardware and are read-only. State consists of clocks, resets, MMIO base, and variant data.

Dependencies/integration: supports PX30/RK3308/RK3528/RK3562/RK3568/RK3576/RK3588 compatibles; depends on reset controller, clock bulk APIs, MMIO polling, and legacy fixed OF cells.

Risks: static `otp_config` is mutated on probe. ECC status errors on RK3568 abort reads with `-EIO`; board cell definitions must account for word-size/read-offset transformations. Reset is performed for some variants on each read, which can be expensive but ensures controller state.

Test signals: variant clock list acquisition, reset failure, ECC enable failure, ECC read error, RK3588 auto-read timeout, partial byte reads from 16/32-bit words, and compatible size/read-offset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/s32g-ocotp-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/s32g-ocotp-nvmem.c

Purpose: NXP S32G OCOTP read-only NVMEM provider with explicit keepout ranges.

Important APIs/types/functions: `struct s32g_ocotp_priv` holds device and MMIO base. `s32g_ocotp_read()` performs sequential 32-bit MMIO reads. `s32g_keepouts[]` defines inaccessible/reserved regions. Probe maps resource and registers NVMEM sized to the resource.

Control flow: probe allocates state, maps resource 0, stores private/device/size in a static NVMEM config, and registers. Reads iterate while at least one full word remains.

State/persistence: OCOTP fuses are persistent in hardware and exposed read-only. Driver state is MMIO mapping and keepout metadata.

Dependencies/integration: OF compatible `nxp,s32g2-ocotp`; uses NVMEM keepout support and legacy fixed cells.

Risks: partial trailing bytes are ignored by the read callback, relying on NVMEM word-size behavior. Keepout ranges are hard-coded and must match the SoC reference manual.

Test signals: keepout enforcement, aligned word reads, resource-size exposure, and attempts to read reserved ranges through fixed cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/s32g-ocotp-nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sc27xx-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/sc27xx-efuse.c

Purpose: Spreadtrum SC27xx PMIC eFuse read-only NVMEM provider using parent regmap and hardware spinlock synchronization.

Important APIs/types/functions: `struct sc27xx_efuse_variant_data` selects PMIC module-enable register. `sc27xx_efuse_lock()` combines a mutex with raw hardware spinlock. `sc27xx_efuse_read()` enables the controller, waits standby, programs block index, starts read, waits done, reads data, clears done, and disables the controller.

Control flow: probe gets parent regmap, reads base from `reg`, obtains a hwspinlock ID and requests it, initializes mutex and variant data, and registers a byte-granular read-only NVMEM sized as 32 two-byte blocks. Reads serialize across local and remote subsystems before touching PMIC registers.

State/persistence: eFuse contents persist in PMIC hardware. Driver state tracks regmap, base, hwspinlock, mutex, and variant register offsets.

Dependencies/integration: compatibles `sprd,sc2731-efuse` and `sprd,sc2730-efuse`; depends on parent regmap, OF hwspinlock binding, and NVMEM fixed cells.

Risks: reads are limited to at most one two-byte block; larger NVMEM requests return `-EINVAL`. The block-index check uses `>` rather than `>=`, so index 32 passes the local test even though max count is 32; NVMEM size should prevent that offset. Remote synchronization depends on the hwspinlock being shared correctly.

Test signals: hwspinlock timeout, standby/read-done poll timeout, variant module-enable address selection, one-byte and two-byte reads with offset shifts, and invalid-size rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sc27xx-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sec-qfprom.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/sec-qfprom.c

Purpose: Secure Qualcomm QFPROM read-only provider that accesses corrected fuse space through SCM calls instead of direct MMIO.

Important APIs/types/functions: `struct sec_qfprom` stores the physical base and device. `sec_qfprom_reg_read()` reads byte-granular data by caching each aligned 32-bit `qcom_scm_io_readl()` result and returning selected bytes. Probe stores resource start as physical base and registers byte-granular NVMEM.

Control flow: probe gets memory resource, sets NVMEM size from it, and registers. Reads iterate per requested byte and invoke SCM whenever the current byte starts a new 32-bit word.

State/persistence: fuses persist in hardware and are exposed read-only. Driver state is the physical base and device pointer.

Dependencies/integration: OF compatible `qcom,sec-qfprom`; depends on Qualcomm SCM firmware and NVMEM legacy fixed cells.

Risks: repeated SCM calls can be slow for large reads. Access failures are mapped to `-EINVAL`, losing detailed firmware status. No explicit root-only flag is set, so permissions follow NVMEM defaults/cell policy.

Test signals: unaligned byte reads across word boundaries, SCM read failure, resource sizing, and fixed-cell consumers for secure-only platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sec-qfprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/snvs_lpgpr.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/snvs_lpgpr.c

Purpose: NVMEM provider for i.MX6/i.MX7 SNVS low-power general-purpose registers.

Important APIs/types/functions: `struct snvs_lpgpr_cfg` provides register offsets and size. `snvs_lpgpr_read()` uses regmap bulk read. `snvs_lpgpr_write()` checks high-power and low-power lock bits before regmap bulk write. Probe resolves the parent syscon regmap and registers 4-byte stride NVMEM.

Control flow: probe verifies OF node, gets compatible config, obtains parent node and syscon regmap, stores config, fills embedded NVMEM config, and registers. Writes first read lock registers and return `-EPERM` if software/hardware lock bits are set.

State/persistence: LPGPR registers reside in secure non-volatile/low-power storage and may survive resets depending on SNVS power domain. Driver state is regmap plus per-SoC offsets.

Dependencies/integration: compatibles `fsl,imx6q-snvs-lpgpr`, `fsl,imx6ul-snvs-lpgpr`, and `fsl,imx7d-snvs-lpgpr`; depends on parent syscon node.

Risks: source contains `struct device_d *dev` in private data, which appears unused and likely a typo but does not affect compiled access paths if accepted by the local tree. Writes are word-count based (`bytes / 4`) and rely on NVMEM alignment.

Test signals: lock-bit write rejection, i.MX6 versus i.MX7 offset/size selection, parent syscon lookup failure, and successful regmap read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/snvs_lpgpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sprd-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/sprd-efuse.c

Purpose: Spreadtrum AP eFuse NVMEM provider with read and permanent program support for the normal eFuse region.

Important APIs/types/functions: `struct sprd_efuse_variant_data` defines normal block count, block offset, and double-data mode. `sprd_efuse_lock()` serializes with mutex and hardware spinlock. `sprd_efuse_raw_read()` controls read power and optional double mode. `sprd_efuse_raw_prog()` writes magic, powers/programs, optionally auto-checks/locks, handles error flags, and clears magic. `sprd_efuse_read()`/`sprd_efuse_write()` are NVMEM callbacks.

Control flow: probe maps MMIO, obtains hwspinlock and enable clock, initializes mutex/variant data, and registers byte-granular read/write NVMEM sized to normal blocks. Reads lock, enable clock, compute physical block as logical offset plus variant offset, read one block, shift/copy requested bytes, disable clock, unlock. Writes lock, enable clock, choose permanent block lock only for full-block writes, program, disable clock, unlock.

State/persistence: eFuse programming is permanent. Runtime state includes clock, lock, MMIO base, and variant geometry.

Dependencies/integration: OF compatible `sprd,ums312-efuse`; depends on hwspinlock, clock, MMIO, and legacy fixed cells.

Risks: write callback passes raw `offset` to `sprd_efuse_raw_prog()` rather than the block index plus normal-block offset used by reads, which is a high-value item to verify against hardware expectations. Full-block writes lock the block against future programming. Power sequencing/magic register handling must unwind on all errors.

Test signals: hwspinlock timeout, clock failure, read error flag clearing, write error flag clearing, partial versus full-block write lock behavior, and verification that logical write offsets map to intended physical blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sprd-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.c

Purpose: OP-TEE client helper for STM32MP BSEC OTP access, used by the STM32 ROMEM NVMEM driver.

Important APIs/types/functions: `stm32_bsec_optee_ta_open()` opens a TEE context and verifies the BSEC TA UUID. `stm32_bsec_optee_ta_read()` invokes `PTA_BSEC_READ_MEM` with aligned shared memory output. `stm32_bsec_optee_ta_write()` invokes `PTA_BSEC_WRITE_MEM` for fuse programming and then lock programming for upper ECC-protected OTPs. Session helpers open/close TA sessions per operation.

Control flow: open checks for OP-TEE GP capability, opens a session to prove TA presence, closes it, and returns the context. Reads open a session, align requested offset/length to 32-bit boundaries, allocate kernel shared memory, invoke the TA, copy requested bytes from the aligned buffer, free shared memory, and close the session. Writes open a session, require 32-bit aligned full words, allocate/copy shared memory, invoke fuse write, optionally rewrite the shared buffer with `LOCK_PERM` words and invoke lock access for upper OTPs, then free and close.

State/persistence: no data cache. The TEE context is retained by the caller; OTP writes and locks are permanent in BSEC hardware.

Dependencies/integration: depends on TEE client API, OP-TEE GP implementation, UUID `94cf71ad-80e6-40b5-a7c6-3dc501eb2803`, and constants shared with `stm32-romem.c`.

Risks: `stm32_bsec_optee_ta_write()` opens a TEE session before validating alignment; the early `return -EINVAL` can leak the session. TA return codes are collapsed to `-EIO` when the kernel invocation itself succeeded but TA returned an error. Writes are permanent and upper OTPs are locked after successful programming.

Test signals: OP-TEE absent causing `-EPROBE_DEFER`, TA session open failure, unaligned read alignment/copy behavior, write alignment rejection with session cleanup, TA access-denied mapping, and upper-lock invocation boundary at `lower * 4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.h -->
# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.h

Purpose: Conditional interface header for STM32 BSEC OP-TEE helper functions.

Important APIs/types/functions: declares `stm32_bsec_optee_ta_open()`, `stm32_bsec_optee_ta_close()`, `stm32_bsec_optee_ta_read()`, and `stm32_bsec_optee_ta_write()` when `CONFIG_NVMEM_STM32_BSEC_OPTEE_TA` is enabled; otherwise provides inline stubs returning `-EOPNOTSUPP`.

Control flow: no runtime flow in the header, but it determines whether `stm32-romem.c` can attempt TA-backed access or must fall back/fail.

State/persistence: no state. The API passes a `struct tee_context *` opaque context opened by the helper and owned by the caller for devm cleanup.

Dependencies/integration: included by both the TA implementation and STM32 ROMEM driver; relies on `struct tee_context` being visible via included headers in users.

Risks: stub behavior makes missing TA support look like a runtime unsupported operation, so probe logic must distinguish optional versus required TA variants. Documentation comments contain minor `nvem` typos only.

Test signals: build coverage with the config enabled and disabled, ROMEM fallback behavior when stubs return `-EOPNOTSUPP`, and correct devm close callback typing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-romem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-romem.c

Purpose: STMicroelectronics STM32 ROMEM/BSEC NVMEM provider for factory-programmed memory and OTPs, supporting plain MMIO, legacy SMC, and OP-TEE PTA access.

Important APIs/types/functions: `struct stm32_romem_cfg` defines size, lower OTP count, and whether TA is required. `stm32_romem_read()` handles simple byte MMIO OTP. `stm32_bsec_read()` reads lower OTPs from shadow MMIO and upper OTPs through SMC. `stm32_bsec_write()` programs OTPs through SMC. `stm32_bsec_pta_read()`/`write()` delegate to OP-TEE helper. Probe selects access mode based on compatible data and OP-TEE/SMC availability.

Control flow: probe maps the resource, fills common NVMEM config, then either exposes simple read-only ROMEM for non-BSEC compatibles or BSEC read/write access. For BSEC, it attempts OP-TEE when required or present; if TA is unavailable and not required, it checks legacy SMC support and falls back to SMC callbacks. Registered NVMEM is byte-granular and OTP typed.

State/persistence: OTP writes are permanent. Lower BSEC words are bitwise/incrementally programmable, while upper words are ECC-protected and word-program-only. Driver state includes MMIO base, lower boundary, NVMEM config, and optional TEE context cleaned by devm.

Dependencies/integration: compatibles `st,stm32f4-otp`, `st,stm32mp15-bsec`, `st,stm32mp13-bsec`, and `st,stm32mp25-bsec`; depends on ARM SMCCC when using SMC, OP-TEE helper when available/required, OF OP-TEE presence detection, and legacy fixed cells.

Risks: write access is exposed for BSEC variants and can permanently program OTPs; the driver warns on upper OTP updates but does not prevent them. TA-required variants fail probe without OP-TEE. SMC support is compile-time gated by `CONFIG_HAVE_ARM_SMCCC`.

Test signals: simple STM32F4 MMIO reads, MP15 OP-TEE fallback to SMC, MP13/MP25 TA-required failure without TA, unaligned reads through SMC/TA, write alignment rejection, upper OTP warning/lock behavior through TA, and devm TEE context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/stm32-romem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sunplus-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/sunplus-ocotp.c

Purpose: Sunplus SP7021 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `struct sp_ocotp_priv` stores two MMIO bases (`hb_gpio`, `otprx`) and a clock. `sp_otp_read_real()` converts byte address to bank/word/byte selection, triggers OTP read, polls `OTP_READ_DONE`, and extracts one byte from HB GPIO data. `sp_ocotp_read()` enables the clock and reads bytes one at a time.

Control flow: probe maps named resources, gets and prepares the clock, fills static NVMEM config, registers, and leaves the clock prepared. Runtime reads enable the clock, loop byte offsets through the low-level read sequence, disable the clock, and return first error.

State/persistence: OTP data is persistent and read-only. State is MMIO base array and clock.

Dependencies/integration: OF compatible `sunplus,sp7021-ocotp`; depends on named resources, clock framework, MMIO polling, and legacy fixed cells.

Risks: per-byte read is slow but simple. The prepared clock is only unprepared on probe failure, not via a remove/devm action in the successful path. Static `sp_ocotp_nvmem_config.size` is fixed to QAC628 size and does not use match data dynamically.

Test signals: named-resource failures, clock prepare/enable failures, read timeout, byte extraction across word/bank boundaries, and fixed-cell reads over multiple bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sunplus-ocotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sunxi_sid.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/sunxi_sid.c

Purpose: Allwinner sunXi Security ID NVMEM provider and entropy contributor.

Important APIs/types/functions: `struct sunxi_sid_cfg` supplies value offset, size, and whether register readout is required. `sunxi_sid_read()` copies directly from SID memory with trailing-byte handling. `sun8i_sid_register_readout()` performs command-based reads through `PRCTL/RDKEY`; `sun8i_sid_read_by_reg()` uses it for H3 unreliable memory window. Probe registers NVMEM and feeds the SID bytes to `add_device_randomness()`.

Control flow: probe selects compatible config, maps MMIO, allocates NVMEM config, chooses direct or register read callback, registers read-only OTP NVMEM, allocates a temporary buffer, reads the full SID, adds it as device randomness, frees the buffer, and stores drvdata.

State/persistence: SID/OTP data persists in SoC hardware. Driver state includes base and value offset; no cache.

Dependencies/integration: many Allwinner compatibles from sun4i A10 through sun50i H6; depends on MMIO polling, NVMEM provider, and kernel random subsystem.

Risks: `.stride = 4` with `.word_size = 1` means core alignment rules must match expected consumers. Adding SID to randomness is useful but should not be treated as secret entropy if IDs are readable. H3 register-read path has a 250 ms poll timeout.

Test signals: direct and register-read variants, trailing byte reads, PRCTL timeout, randomness path allocation failure, and compatible-specific sizes/value offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/sunxi_sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/u-boot-env.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/u-boot-env.c

Purpose: MTD-backed NVMEM provider for U-Boot environment storage, coupled with the U-Boot environment layout parser.

Important APIs/types/functions: `struct u_boot_env` stores device, registered NVMEM device, format, and `struct mtd_info`. `u_boot_env_read()` wraps `mtd_read()` and tolerates bitflip return codes. Probe gets the MTD device for the OF node, registers an NVMEM provider sized to the MTD, then calls `u_boot_env_parse()`.

Control flow: probe allocates state, stores format from OF match data, resolves the MTD partition/device node, registers a read-only NVMEM provider with custom read callback, and immediately parses environment variables into NVMEM cells. Runtime reads are direct MTD reads with short-read detection.

State/persistence: environment data persists in MTD flash. Driver state references the MTD and NVMEM device; variable cells are registered by the layout parser.

Dependencies/integration: OF compatibles mirror layout formats; depends on MTD, NVMEM provider, and `layouts/u-boot-env.h`.

Risks: the MTD device acquired by `of_get_mtd_device_by_node()` is not explicitly released in this file, so lifetime management should be checked against devm/platform expectations. Registering NVMEM before parsing means parse failure returns probe failure after provider registration is devm-managed. Bitflips are accepted but still may indicate marginal flash.

Test signals: MTD lookup deferral/failure, bitflip-tolerant reads, short reads, parser CRC failures propagating from probe, and per-format compatible selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/u-boot-env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/uniphier-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/uniphier-efuse.c

Purpose: Socionext UniPhier eFuse read-only NVMEM provider.

Important APIs/types/functions: `struct uniphier_efuse_priv` stores MMIO base. `uniphier_reg_read()` copies bytes with `readb()`. Probe maps resource, sizes from resource, and registers byte-granular read-only NVMEM with legacy fixed OF cells.

Control flow: probe allocates private state, maps resource 0, fills local `nvmem_config`, and registers. Runtime reads are simple byte loops from base plus offset.

State/persistence: eFuse data persists in hardware and is read-only. Driver keeps no cache.

Dependencies/integration: OF compatible `socionext,uniphier-efuse`; uses platform MMIO and NVMEM provider APIs.

Risks: no special locking, power, or clock control is present, so the mapped block must be always accessible. Byte loop is simple but less efficient for large reads.

Test signals: resource-size exposure, byte and multi-byte fixed-cell reads, and probe failure for missing resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/uniphier-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/vf610-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/vf610-ocotp.c

Purpose: Freescale/NXP Vybrid VF610 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `base_to_fuse_addr_mappings` maps sparse MMIO offsets to fuse addresses. `vf610_ocotp_calculate_timing()` computes timing fields from the clock rate. `vf610_ocotp_wait_busy()` polls `BUSY` and clears `ERR` on timeout. `vf610_ocotp_read()` maps offsets, programs timing/address/read command, waits, and returns fuse data or zero for unmapped offsets.

Control flow: probe maps the OCOTP resource, gets the clock, computes timing once, fills static NVMEM config sized to the resource, and registers. Reads loop 4-byte chunks, skip unknown offset mappings as zero, and do not enable/disable the clock around reads.

State/persistence: OTP fuses persist in hardware and are read-only. Driver state includes timing derived from the clock rate.

Dependencies/integration: OF compatible `fsl,vf610-ocotp`; depends on clock framework, MMIO, and NVMEM provider.

Risks: `vf610_get_fuse_address()` returns zero for the first valid fuse address, but `vf610_ocotp_read()` only treats `fuse_addr > 0` as valid, so the mapping for fuse address 0 is skipped and returned as zero. Clock rate changes after probe are not reflected in timing. Hardware read errors are logged but the returned TRM error value is still passed to consumers.

Test signals: mapping table coverage including offset `0x400`, timing calculation at expected clock rates, busy timeout, error-bit handling, and reads from unmapped offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/vf610-ocotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/zynqmp_nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/zynqmp_nvmem.c

Purpose: Xilinx/AMD ZynqMP firmware-backed NVMEM provider for silicon revision and eFuse/PUF user fuse access.

Important APIs/types/functions: `struct xilinx_efuse` is the DMA-shared firmware request descriptor. `zynqmp_efuse_access()` validates alignment and PUF bit restrictions, allocates coherent descriptor/data buffers, calls `zynqmp_pm_efuse_access()`, and copies read data back. `zynqmp_nvmem_read()` special-cases silicon revision through `zynqmp_pm_get_chipid()` and routes eFuse ranges to firmware. `zynqmp_nvmem_write()` permits firmware writes in eFuse ranges.

Control flow: probe registers a byte-granular NVMEM config sized to include SoC version, unused gap, and eFuse region. Reads at offset 0 return masked silicon revision; eFuse and PUF ranges call firmware; other offsets return `0xDEADBEEF`. Writes reject offsets outside eFuse/PUF ranges and otherwise call firmware with write flag.

State/persistence: eFuse writes are permanent. Driver keeps no private state beyond using `struct device` as callback context.

Dependencies/integration: OF compatible `xlnx,zynqmp-nvmem-fw`; depends on Xilinx firmware API and DMA-coherent memory allocation.

Risks: firmware error `EFUSE_NOT_ENABLED` maps to `-EOPNOTSUPP`, other firmware errors to `-EPERM`. Returning `0xDEADBEEF` for unsupported read offsets may mask bad cell definitions. PUF row bitmask restrictions are enforced only for specific offsets.

Test signals: silicon revision read size check, word alignment rejection, PUF mask rejection, firmware disabled/error paths, DMA allocation failures, and default-gap reads returning sentinel value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/zynqmp_nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/of/Kconfig

Purpose: Kconfig definitions for Linux Device Tree/Open Firmware infrastructure.

Important APIs/types/functions: defines core `menuconfig OF` and feature symbols including `OF_UNITTEST`, `OF_KUNIT_TEST`, `OF_ALL_DTBS`, `OF_FLATTREE`, `OF_EARLY_FLATTREE`, `OF_DYNAMIC`, `OF_ADDRESS`, `OF_IRQ`, `OF_RESERVED_MEM`, `OF_RESOLVE`, `OF_OVERLAY`, `OF_OVERLAY_KUNIT_TEST`, and `OF_NUMA`.

Control flow: Kconfig dependencies/selects drive which OF source files build. `OF_EARLY_FLATTREE` defaults on for most OF platforms and selects `OF_FLATTREE`; `OF_ADDRESS` defaults on except SPARC when `HAS_IOMEM` or UML is present; overlay/unit-test options select required resolver/dtc support.

State/persistence: no runtime state; persistent effect is the generated kernel configuration and compiled object set.

Dependencies/integration: consumed by `drivers/of/Makefile` and architecture/platform Kconfig selections. Test options integrate with KUnit and boot-time OF unittest infrastructure.

Risks: `OF_UNITTEST` help explicitly warns it taints the kernel and can corrupt the live devicetree; it should remain development-only. Select chains can pull in DTC/LIBFDT/CRC32 and alter build footprint.

Test signals: config matrix builds for OF disabled/enabled, KUnit tests, overlays, all-DTB compile testing, and architecture exclusions for early flattree/address support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/Makefile -->
# sources/distributed-fs/ceph-client/drivers/of/Makefile

Purpose: Object list controlling which OF infrastructure components build for each Kconfig symbol.

Important APIs/types/functions: always builds `base.o cpu.o device.o module.o platform.o property.o`; conditionally includes `kobj.o`, `dynamic.o`, `fdt.o`, `fdt_address.o`, `pdt.o`, `address.o`, `irq.o`, `unittest.o`, reserved memory, resolver, overlay, NUMA, kexec, KUnit helpers/tests, overlay tests, and unittest data.

Control flow: kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` entries after Kconfig resolution. Nested `CONFIG_KEXEC_FILE` and `CONFIG_OF_FLATTREE` add `kexec.o` only when both are enabled.

State/persistence: no runtime state; determines compiled artifacts and link order.

Dependencies/integration: directly aligned with `drivers/of/Kconfig`. Overlay KUnit test builds a composite `overlay-test-y` from code and DTBO object.

Risks: missing or mismatched Kconfig guards would produce unresolved symbols or omit required OF helpers. Link order matters for built-in initialization and test data availability.

Test signals: build all relevant Kconfig combinations, especially OF address without PCI, overlay KUnit, KEXEC_FILE+FLATTREE, and OF_UNITTEST data inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/address.c -->
# sources/distributed-fs/ceph-client/drivers/of/address.c

Purpose: Core OF address translation and resource construction logic. It converts device-tree `reg`, `ranges`, `dma-ranges`, PCI/ISA address encodings, and MMIO/PIO resources into CPU physical addresses, DMA regions, and kernel `struct resource` objects.

Important APIs/types/functions: `struct of_bus` abstracts bus-specific cell counting, mapping, translation, and flag extraction. Exported APIs include `of_translate_address()`, `of_translate_dma_address()`, `of_translate_dma_region()`, `__of_get_address()`, `of_property_read_reg()`, `of_pci_range_parser_init()`, `of_pci_dma_range_parser_init()`, `of_pci_range_parser_one()`, `of_dma_get_range()`, `of_dma_get_max_cpu_address()`, `of_dma_is_coherent()`, `of_address_to_resource()`, `of_pci_address_to_resource()`, `of_iomap()`, and `of_io_request_and_map()`. `__of_address_resource_bounds()` is visible to KUnit and checks `struct resource` overflow.

Control flow: translation starts by matching the parent bus, counting address/size cells, copying the input address, then walking parent nodes. Each level chooses the parent bus, handles logical PIO host ranges, applies `ranges` or `dma-ranges` through `of_translate_one()`, and updates the address cells until root is reached. Resource conversion fetches the selected `reg` or PCI BAR address, translates memory or I/O space, applies optional nonposted MMIO flags, and fills bounded resource start/end.

State/persistence: no persistent mutable state except a static cached PowerMac empty-ranges quirk result. Parsers carry iteration state over property cell arrays. Mapping helpers create runtime ioremap mappings and resource reservations for callers.

Dependencies/integration: central dependency for platform bus probing, PCI host bridge resources, DMA setup, reserved/translated MMIO consumers, logic PIO, KUnit overflow tests, and architecture DMA coherency defaults. Conditional PCI and DMA sections compile based on `CONFIG_PCI` and `CONFIG_HAS_DMA`.

Risks: address-cell and size-cell validation is critical; bad DT properties return `OF_BAD_ADDR` or `-EINVAL`. Empty `ranges` semantics include historical PowerPC/Apple quirks and special `dma-ranges` handling. I/O space translation can fail if PCI I/O ranges are not registered early enough. DMA range parsing allocates a sentinel-terminated map and must skip untranslatable ranges. Overflow handling protects resource bounds but consumers must check return values.

Test signals: KUnit for `__of_address_resource_bounds()` overflow and zero-size behavior; DT tests for default, default-flags, ISA, and PCI bus mappings; missing versus empty `ranges`; `dma-ranges` ancestry and `interconnects` `dma-mem` parent selection; I/O port translation with logic PIO; nonposted MMIO flag propagation; and `of_iomap()`/`of_io_request_and_map()` success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/address.c -->
