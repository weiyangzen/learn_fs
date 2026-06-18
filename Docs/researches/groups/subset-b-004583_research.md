# subset-b-004583 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.c

Purpose: implements the generic Microsemi/Microchip Ocelot VCAP programming layer for IS1, IS2, and ES0 TCAM blocks. It converts `struct ocelot_vcap_filter` objects into packed key/action/counter cache words, mirrors software rule order into hardware TCAM rows, initializes VCAP memories, and manages IS2 auxiliary resources such as policers and mirror sessions.

Important APIs and types: internal `struct vcap_data` holds cache-format entry, mask, action, counter, type-group, and per-subword offsets. Exported APIs include `ocelot_vcap_init`, `ocelot_vcap_filter_add`, `ocelot_vcap_filter_del`, `ocelot_vcap_filter_replace`, `ocelot_vcap_filter_stats_update`, `ocelot_vcap_block_find_filter_by_id`, `ocelot_vcap_policer_add`, and `ocelot_vcap_policer_del`. Packing helpers include `vcap_key_set`, `vcap_key_bytes_set`, `vcap_key_bit_set`, `vcap_action_set`, and block-specific encoders `is1_entry_set`, `is2_entry_set`, and `es0_entry_set`.

Control flow: `ocelot_vcap_init` programs a discard policer, initializes rule lists, detects hardware constants from `VCAP_CONST_*`, and clears each VCAP block. Add/delete operations first update the software list sorted by priority, then rewrite affected hardware entries to preserve ordering. Adds shift lower-priority entries down, reading counters before moves; deletes remove auxiliary resources, shift following entries up, and clear the duplicated tail entry. Stats update reads the hardware counter, copies it to `filter->stats.pkts`, then rewrites the entry with a zero counter.

State and persistence: persistent runtime state is in `ocelot->block[*].rules`, `block->count`, `ocelot->vcap[*]` hardware constants, and `ocelot->vcap_pol.pol_list`. The actual hardware state is volatile TCAM/cache/counter memory and policer configuration. The policer list uses refcounts so multiple filters can share a policer index.

Dependencies and integration: depends on Ocelot core register helpers, `struct vcap_props` field maps, Linux lists/refcounts, `qos_policer_conf_set`, mirror helpers, and TC flower offload users that allocate `struct ocelot_vcap_filter`. `vsc7514_regs.c` supplies the field offsets consumed here.

Risks: bit-level packing is sensitive to field widths, type-group offsets, byte order, and action table counts. IS2 MAC_ETYPE classification has a hardware limitation: MAC_ETYPE rules for ARP/IP/SNAP-style frames cannot be mixed with non-MAC_ETYPE rules on the same port/lookup, so the code enforces exclusivity. `vcap_cmd` silently returns for out-of-range entry selections. Counter preservation during entry moves is important to avoid losing packet stats.

Test signals: exercise TC flower rules for VLAN, MAC, ARP, IPv4, IPv6, TCP/UDP ports, mirror, police/drop, replace/delete, and stats reads. Validate priority ordering, rule movement, counter clearing, policer refcount behavior, and rejection of incompatible IS2 key mixtures through extack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.h

Purpose: private Ocelot VCAP header that exposes the local VCAP initialization, stats, and TC flower setup entry points used by the mscc Ethernet driver pieces. It bridges driver-private Ocelot types with the shared SoC VCAP definitions.

Important APIs/types: defines `OCELOT_POLICER_DISCARD` as `0x17f`, the reserved policer used by `ocelot_vcap_init` and ACL drop actions. Declares `ocelot_vcap_filter_stats_update`, `ocelot_vcap_init`, and `ocelot_setup_tc_cls_flower`.

Control flow: this file has no executable flow; it constrains call visibility and include ordering. Implementations live in `ocelot_vcap.c` and TC flower code elsewhere.

State and persistence: no direct state. The discard policer constant is a durable contract with the VCAP code and hardware policer range configured by the platform.

Dependencies and integration: includes driver-private `ocelot.h`, shared `<soc/mscc/ocelot_vcap.h>`, and `<net/flow_offload.h>`. It is consumed by Ocelot port/TC integration code that needs to initialize VCAP and translate flower classifiers.

Risks: changing the discard policer value without matching platform limits or QoS policer setup can break ACL drop semantics. Prototype drift would break VCAP/TC integration at compile time.

Test signals: build coverage for `CONFIG_MSCC_OCELOT_SWITCH` paths and runtime TC flower drop/stat rules that depend on `OCELOT_POLICER_DISCARD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vsc7514.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vsc7514.c

Purpose: platform driver for the VSC7514 Ocelot switch. It binds the device-tree compatible `mscc,vsc7514-switch`, maps hardware targets, initializes the common Ocelot core, creates ports/devlink objects, enables optional FDMA/PTP support, and registers switchdev/netdevice notifiers.

Important APIs/functions: `ocelot_chip_init` selects `vsc7514_regmap`, initializes regfields, PLL, ops, MAC seed, and MACT sizing. IRQ handlers are `ocelot_xtr_irq_handler` for CPU-frame extraction and `ocelot_ptp_rdy_irq_handler` for TX timestamp readiness. `mscc_ocelot_init_ports` maps per-port resources, initializes physical or unused devlink ports, and calls `ocelot_probe_port`. `mscc_ocelot_probe` is the main bring-up path; `mscc_ocelot_remove` unwinds it.

Control flow: probe allocates a devlink-private `struct ocelot`, maps named IO targets (`sys`, `rew`, `qsys`, `ana`, `qs`, `s0`, `s1`, `s2`, plus optional `ptp` and `fdma`), resolves HSIO syscon, initializes chip state, requests extraction and optional PTP IRQs, parses `ethernet-ports`, assigns VCAP props and policer range, calls `ocelot_init`, probes ports, starts FDMA, registers shared-buffer devlink resources, optionally initializes timestamping, registers switchdev notifiers, then registers devlink. Remove reverses FDMA, devlink, timestamp, shared-buffer, port, notifier, and devlink allocation state.

State and persistence: runtime state lives under `struct ocelot`: target regmaps, per-port pointers, devlink ports, VCAP properties, policer base/max, FDMA/PTP flags, and notifier registration. No persistent disk state; all hardware configuration is reconstructed on probe.

Dependencies and integration: depends on platform resources, OF graph children, `vsc7514_regs.c` exports, Ocelot core APIs, phylink/netdevice/switchdev/devlink, optional FDMA, and PTP clock operations.

Risks: probe error unwinding spans many subsystems; missed teardown can leak devlink ports or registered netdevices. Optional target handling must leave `PTP`/`FDMA` null safely. `ocelot_xtr_irq_handler` must drain CPU queues on frame extraction errors to prevent interrupt storms or stuck RX state.

Test signals: device-tree probe on VSC7514 hardware or emulation, invalid/missing port resources, FDMA absent/present, PTP absent/present, frame extraction IRQ delivery, devlink port inventory, switchdev bridge operations, and clean module/platform removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vsc7514.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/vsc7514_regs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/vsc7514_regs.c

Purpose: VSC7514 register and VCAP layout description used by the generic Ocelot core. It maps symbolic register IDs to target offsets, defines replicated regfields, and provides field offsets/widths for ES0, IS1, and IS2 VCAP keys/actions.

Important exports: `vsc7514_regfields`, `vsc7514_regmap`, and `vsc7514_vcap_props`. Internal tables cover ANA, QS, QSYS, REW, SYS, VCAP, PTP, DEV_GMII register targets and VCAP field tables for ES0/IS1/IS2. `vsc7514_vcap_props` associates ES0 with target S0, IS1 with S1, and IS2 with S2, including action type widths and action layout counts.

Control flow: no executable control flow beyond static initialization. Ocelot probe assigns these tables into `ocelot->map` and `ocelot->vcap`; later core helpers index into them for `regmap` access and VCAP bit packing.

State and persistence: all data is immutable after load. The tables encode a hardware ABI: offsets, bit positions, replicated register counts, and action/key widths. Hardware runtime state is not stored here.

Dependencies and integration: includes shared Ocelot VCAP and VSC7514 register definitions plus the private Ocelot header. It is consumed by `ocelot_vsc7514.c`, generic Ocelot register helpers, and `ocelot_vcap.c` packing logic.

Risks: wrong offsets or field widths create silent hardware misprogramming. The IS1 action table explicitly notes manual fields shifted by 2, so future edits must preserve driver-verified corrections rather than blindly matching datasheet text. VCAP key overlap is intentional for type-specific layouts; accidental field reuse changes can corrupt classifier behavior.

Test signals: register smoke tests on probe, TC flower rules covering ES0 VLAN tag rewrites, IS1 classification actions, IS2 ACL actions, PTP register use, MAC learning/flooding paths, and comparisons of programmed hardware behavior against expected field maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/vsc7514_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Kconfig

Purpose: Kconfig menu for Mucse Ethernet devices. It gates visibility of Mucse-specific drivers behind `NET_VENDOR_MUCSE` and defines the `MGBE` tristate for the rnpgbe PCIe 1GbE adapter driver.

Important symbols: `NET_VENDOR_MUCSE` is a vendor-menu boolean defaulting to `y`. `MGBE` is a tristate depending on `PCI`; when built as a module, the module name is `rnpgbe`.

Control flow: configuration-only. If the vendor option is disabled, the `MGBE` prompt is hidden and the Makefiles will not include rnpgbe objects.

State and persistence: persistent effect is the generated kernel `.config`, which controls compilation and module availability.

Dependencies and integration: integrated from the broader Ethernet vendor Kconfig tree. The help text points to `Documentation/networking/device_drivers/ethernet/mucse/rnpgbe.rst`.

Risks: `MGBE` has no explicit dependency on firmware mailbox support beyond PCI, so compile-time coverage must catch missing includes. The vendor default of `y` exposes the driver prompt broadly.

Test signals: Kconfig olddefconfig/menuconfig coverage for built-in, module, and disabled modes; verify `CONFIG_MGBE=m` builds `rnpgbe.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Makefile

Purpose: vendor-level kernel build glue for Mucse Ethernet drivers.

Important declarations: `obj-$(CONFIG_MGBE) += rnpgbe/` descends into the rnpgbe subdirectory when the driver is enabled.

Control flow: Make/Kbuild only. The parent networking Makefile includes this directory; Kbuild conditionally visits `rnpgbe/`.

State and persistence: no runtime state. Build artifacts depend on `CONFIG_MGBE`.

Dependencies and integration: pairs with `mucse/Kconfig` and `mucse/rnpgbe/Makefile`.

Risks: symbol mismatch with Kconfig would silently skip or always build the driver. Current mapping is direct and minimal.

Test signals: kernel build with `CONFIG_MGBE=y`, `m`, and unset; verify `rnpgbe_main.o`, `rnpgbe_chip.o`, `rnpgbe_mbx.o`, and `rnpgbe_mbx_fw.o` are included only when intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/Makefile

Purpose: Kbuild file for the Mucse rnpgbe driver module.

Important declarations: `obj-$(CONFIG_MGBE) += rnpgbe.o` builds a composite object. `rnpgbe-objs` links `rnpgbe_main.o`, `rnpgbe_chip.o`, `rnpgbe_mbx.o`, and `rnpgbe_mbx_fw.o`.

Control flow: build-time only; it defines link composition and module naming.

State and persistence: no runtime state. The linked module contains PCI netdev glue, board initialization, raw mailbox transport, and firmware command wrappers.

Dependencies and integration: invoked through the vendor Makefile when `CONFIG_MGBE` is enabled.

Risks: adding new source files without extending `rnpgbe-objs` will compile nothing into the module. Link ordering is simple and currently does not rely on initcall order.

Test signals: `make M=drivers/net/ethernet/mucse/rnpgbe` or full kernel build for both built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe.h

Purpose: central private header for the Mucse rnpgbe 1GbE PCIe driver. It defines board IDs, core hardware/mailbox state, driver-private netdev state, public internal function prototypes, PCI device IDs, and a simple MMIO write helper.

Important APIs/types: `enum rnpgbe_boards` distinguishes N500 and N210 board families. `struct mucse_mbx_info` stores mailbox timing, counters, lock, shared-memory base, and control/mask offsets. `struct mucse_hw` stores MMIO base, PCI device, mailbox, port, and PF/VF number. `struct mucse` is netdev private state with `netdev`, `pdev`, `hw`, and `stats`. Prototypes connect `rnpgbe_main.c`, `rnpgbe_chip.c`, and firmware mailbox code.

Control flow: no executable flow, but the structs shape probe-time initialization and mailbox request paths.

State and persistence: runtime state is in `struct mucse` allocated by `alloc_etherdev_mq`. Mailbox counters `fw_req` and `fw_ack` mirror firmware registers and are used to detect new messages/acks.

Dependencies and integration: includes Linux types and mutex support. Used by all rnpgbe translation units.

Risks: `mucse_hw_wr32` performs unchecked MMIO offset writes relative to BAR mapping; board-specific offsets must be initialized first. `struct mucse_stats` currently only tracks dropped TX, matching the minimal transmit implementation.

Test signals: compile coverage and probe on each PCI ID; inspect netdev private state after init; verify valid MAC path and fallback random MAC path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_chip.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_chip.c

Purpose: board-level hardware helper layer for rnpgbe. It initializes board-specific mailbox bases, resets hardware through firmware, sends power notifications, and retrieves the permanent MAC address.

Important functions: `rnpgbe_get_permanent_mac` calls `mucse_mbx_get_macaddr` and validates the address. `rnpgbe_reset_hw` disables `RNPGBE_DMA_AXI_EN` before asking firmware to reset hardware. `rnpgbe_send_notify` dispatches notification modes, currently only `mucse_fw_powerup`. `rnpgbe_init_hw` chooses N500/N210 bases and initializes PF mailbox parameters.

Control flow: probe calls `rnpgbe_init_hw`, then power-up notify, firmware sync, reset, and MAC retrieval. Board init sets `hw->port = 0`, common mailbox control/mask offsets, then family-specific control/shared-memory bases.

State and persistence: mutates `struct mucse_hw` and `struct mucse_mbx_info` only. Hardware reset and power notifications affect device/firmware state but are not persisted by the driver.

Dependencies and integration: depends on `rnpgbe_hw.h` offsets, raw mailbox transport from `rnpgbe_mbx.c`, firmware commands from `rnpgbe_mbx_fw.c`, PCI device logging, and Ethernet address validation.

Risks: all board types currently force `hw->port = 0`; multi-port devices may need a reliable port derivation. Reset disables DMA before firmware reset; failures after this point can leave degraded hardware state. Unsupported board type returns `-EINVAL`.

Test signals: probe each supported device ID, firmware reset success/failure, invalid MAC fallback behavior, power-up/power-down notification logs, and mailbox base validation for N500 vs N210.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_hw.h

Purpose: hardware constants for rnpgbe board families and core queue/MMIO settings.

Important declarations: N500 and N210 firmware-to-PF control/shared-memory bases, common PF-to-FW mailbox control and mask offsets, `RNPGBE_DMA_AXI_EN`, and `RNPGBE_MAX_QUEUES` set to 8.

Control flow: no executable flow. Constants are consumed by `rnpgbe_chip.c` and `rnpgbe_main.c`.

State and persistence: none directly; constants define runtime MMIO address calculations.

Dependencies and integration: included by board and PCI netdev code.

Risks: incorrect offsets break mailbox synchronization and reset paths. Queue count must match `alloc_etherdev_mq` usage and any future real TX/RX queue implementation.

Test signals: BAR2 MMIO sanity on both N500 and N210 hardware, mailbox command success, and queue count consistency in netdev registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_main.c

Purpose: PCI driver and minimal netdev implementation for Mucse rnpgbe adapters. It detects supported PCI IDs, enables PCI resources, maps BAR2, initializes firmware communication, registers a netdev, and handles remove/shutdown.

Important functions: `rnpgbe_probe`, `rnpgbe_add_adapter`, `rnpgbe_rm_adapter`, `rnpgbe_remove`, `rnpgbe_shutdown`, and netdev ops `rnpgbe_open`, `rnpgbe_close`, `rnpgbe_xmit_frame`. The PCI ID table maps Mucse N210/N210L/N500 dual/N500 quad IDs to board families.

Control flow: probe enables memory decoding, sets a 56-bit coherent DMA mask, requests memory regions, sets bus mastering, saves PCI state, and calls `rnpgbe_add_adapter`. Adapter setup allocates an 8-queue Ethernet device, maps BAR2, initializes board/mailbox state, sends firmware power-up, synchronizes firmware, resets hardware, gets or generates MAC, and registers the netdev. Remove unregisters the netdev, sends power-down, frees it, releases regions, and disables PCI.

State and persistence: per-device state is `struct mucse` in netdev private memory. TX path currently drops every skb, increments `mucse->stats.tx_dropped`, and returns `NETDEV_TX_OK`; no RX rings, interrupts, or persistent queues are implemented.

Dependencies and integration: uses PCI core, DMA mask APIs, rtnl for shutdown, Ethernet helpers, and rnpgbe mailbox/chip helpers.

Risks: this is not yet a functional data-plane driver; TX is a drop sink and open/close are no-ops. `rnpgbe_dev_shutdown` dereferences `mucse` without a null check. Error paths only power down if power-up notification succeeded, which is intentional but should be verified. BAR index 2 is assumed.

Test signals: PCI bind/unbind, probe failure injection at BAR map, firmware sync/reset/MAC errors, `ip link set up/down`, transmit counters showing drops, shutdown path, and random MAC fallback only for invalid firmware MAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.c

Purpose: low-level PF-to-firmware mailbox transport for rnpgbe. It performs MMIO reads/writes to shared memory/control registers, arbitrates ownership with PFU/REQ bits, tracks firmware request/ack counters, and provides blocking read/write helpers.

Important functions: `mucse_write_and_wait_ack_mbx`, `mucse_poll_and_read_mbx`, and `mucse_init_mbx_params_pf` are externally visible. Internal helpers handle data/control MMIO, lock acquisition/release, counter extraction/increment, polling for messages, polling for acks, and reset of local mailbox state.

Control flow: writes acquire the PF mailbox lock through `read_poll_timeout_atomic`, copy u32 words into shared memory, snapshot current FW ack, increment PF request, and release the lock with `MUCSE_MBX_REQ` set. The caller then polls for a changed nonzero FW ack. Reads poll for a changed nonzero FW request, acquire the lock, copy shared memory into the caller buffer, clear the first data word, snapshot FW request, increment PF ack, and release without request.

State and persistence: `hw->mbx.fw_req` and `fw_ack` are local snapshots used to identify new mailbox events. `mbx->lock` serializes higher-level firmware command exchanges; lower-level PFU ownership serializes shared memory with firmware. Hardware counters persist until reset.

Dependencies and integration: uses Linux `read_poll_timeout`, `read_poll_timeout_atomic`, bitfield helpers, and mailbox offsets from `rnpgbe_mbx.h` and board initialization.

Risks: `size` is divided by four, so non-u32-aligned sizes would silently truncate. Polling treats zero counters as reset/error, which may be fragile across firmware behavior. Raw MMIO has no bounds checking against mailbox buffer size. Atomic lock polling allows IRQ-context use, but higher-level wrappers also use a mutex and therefore are process-context only.

Test signals: firmware command round trips, timeout handling when firmware is absent, reset register behavior, concurrent command serialization, ack/request counter wraparound, and malformed size tests under instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.h

Purpose: low-level mailbox register layout and transport prototypes for rnpgbe.

Important declarations: defines FW-to-PF and PF-to-FW counter offsets, shared-memory offset, mailbox control/mask access macros, `MUCSE_MBX_REQ`, and `MUCSE_MBX_PFU`. Declares write-wait-ack, init, and poll-read functions.

Control flow: no executable flow; constants drive `rnpgbe_mbx.c`.

State and persistence: no direct state. The constants name hardware bits and offsets whose values persist in device registers during runtime.

Dependencies and integration: includes `rnpgbe.h` for `struct mucse_hw` and mailbox structure.

Risks: PFU/REQ bit definitions are ownership protocol-critical. Incorrect counter offsets would invert request/ack handling.

Test signals: compile coverage plus firmware mailbox command tests that prove PFU acquisition, request notification, and ack detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.c

Purpose: firmware-command layer over the rnpgbe mailbox transport. It builds packed firmware request/reply structs for hardware info, power state, reset, and MAC address commands.

Important functions: `mucse_fw_send_cmd_wait_resp` serializes request/response commands under `hw->mbx.lock`. Public wrappers are `mucse_mbx_sync_fw`, `mucse_mbx_powerup`, `mucse_mbx_reset_hw`, and `mucse_mbx_get_macaddr`; internal `mucse_mbx_get_info` stores the PF/VF number returned by firmware.

Control flow: request/response commands write the request, wait for firmware ack, then poll/read replies up to three attempts until opcode matches. Nonzero reply error codes become `-EIO`; opcode mismatch after retries becomes `-ETIMEDOUT`. Sync retries hardware-info requests on timeout. Power-up sends only the request and waits for ack, not a full reply.

State and persistence: mutates `hw->pfvfnum` after `GET_HW_INFO`. Power-up/power-down and reset affect firmware/hardware state. No persistent host storage.

Dependencies and integration: depends on packed structs and opcodes from `rnpgbe_mbx_fw.h`, raw transport from `rnpgbe_mbx.c`, endian helpers, and Ethernet address copying by chip code.

Risks: `reply->opcode` and `reply->error_code` are little-endian fields but are compared/read directly in places; this is harmless only on little-endian hosts or if firmware/native layout matches. The retry loop permits four reads because it decrements after the condition. `mucse_mbx_get_macaddr` trusts `port` as an index into four reply addresses.

Test signals: command success/failure for `GET_HW_INFO`, `POWER_UP`, `RESET_HW`, `GET_MAC_ADDRESS`; endian/static analysis; timeout injection; invalid port/port-mask responses; and verify `pfvfnum` feeds MAC request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.h

Purpose: firmware mailbox ABI definitions for rnpgbe.

Important declarations: `MUCSE_MBX_REQ_HDR_LEN`, opcodes `GET_HW_INFO`, `GET_MAC_ADDRESS`, `RESET_HW`, and `POWER_UP`; packed `struct mucse_hw_info`, `struct mbx_fw_cmd_req`, and `struct mbx_fw_cmd_reply`; prototypes for firmware command helpers.

Control flow: no executable flow. The request union carries power-up and MAC-address payloads; the reply union carries raw data, MAC address arrays, or hardware info.

State and persistence: ABI structs define transient mailbox messages. Fields like `fw_version`, `pfnum`, and MAC addresses describe firmware/device state consumed during probe.

Dependencies and integration: includes Linux types and `rnpgbe.h`. Used by `rnpgbe_mbx_fw.c`, `rnpgbe_chip.c`, and `rnpgbe_main.c`.

Risks: packed ABI must match firmware exactly. Endianness annotations require callers to use `cpu_to_le*`/`le*_to_cpu`; direct comparisons are a review hotspot. The MAC reply supports four ports, so port validation must happen before indexing.

Test signals: compile-time struct size checks if added, firmware round-trip tests, endian sparse warnings, and MAC/hardware-info decoding on all supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Kconfig

Purpose: Kconfig menu for Myricom Ethernet devices, especially the Myri-10G PCI driver and optional Direct Cache Access support.

Important symbols: `NET_VENDOR_MYRI` depends on `PCI && INET` and gates the menu. `MYRI10GE` is a tristate selecting `FW_LOADER` and `CRC32`. `MYRI10GE_DCA` is a boolean depending on `MYRI10GE`, `DCA`, and a built-in/module compatibility expression.

Control flow: configuration-only. Enabling `MYRI10GE` builds the driver and exposes module firmware dependencies; enabling DCA compiles additional DCA notifier and tag-writing paths.

State and persistence: generated `.config` controls built-in/module inclusion and optional DCA behavior.

Dependencies and integration: ties to the Myricom Makefile and kernel firmware loader. Help text documents external firmware requirements for older EEPROMs.

Risks: DCA dependency must avoid built-in driver depending on module-only DCA. Firmware loader and CRC32 selects are required by `myri10ge.c` hotplug firmware validation.

Test signals: Kconfig resolution for `MYRI10GE=y/m/n`, DCA enabled/disabled, and module build containing `MODULE_FIRMWARE` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Makefile

Purpose: vendor-level Kbuild glue for Myricom Ethernet support.

Important declaration: `obj-$(CONFIG_MYRI10GE) += myri10ge/` descends into the Myri-10G driver directory when configured.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: paired with `myricom/Kconfig` and `myricom/myri10ge/Makefile`.

Risks: symbol mismatch would prevent driver compilation. The file currently has a single target, so behavior is straightforward.

Test signals: kernel builds with `CONFIG_MYRI10GE` set to built-in, module, and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/Makefile

Purpose: Kbuild file for the Myricom Myri-10G Ethernet driver.

Important declaration: `obj-$(CONFIG_MYRI10GE) += myri10ge.o` builds the single-source driver object/module.

Control flow: build-time only; all behavior is in `myri10ge.c`.

State and persistence: no runtime state.

Dependencies and integration: invoked from the Myricom vendor Makefile.

Risks: if the driver is split into more source files later, this file must be updated to a composite object declaration.

Test signals: `make M=drivers/net/ethernet/myricom/myri10ge` and full kernel builds in module and built-in modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge.c

Purpose: full Myricom Myri-10G Ethernet PCI driver. It manages firmware loading/adoption, the MCP command ABI, RX/TX DMA rings, NAPI polling, MSI/MSI-X queue slicing, ethtool operations, multicast/MAC/MTU controls, watchdog recovery, suspend/resume, and optional DCA.

Important types/functions: `struct myri10ge_priv` is device-global state; `struct myri10ge_slice_state` owns per-queue TX/RX rings, NAPI, IRQ/stat DMA, and DCA fields; `myri10ge_send_cmd` is the central firmware command path. Probe/remove are `myri10ge_probe` and `myri10ge_remove`; open/close are `myri10ge_open` and `myri10ge_close`; data path is `myri10ge_xmit`, `myri10ge_intr`, `myri10ge_poll`, `myri10ge_clean_rx_done`, and `myri10ge_rx_done`.

Control flow: probe enables PCI, sets read-request and DMA masks, maps SRAM WC, parses EEPROM strings for MAC/product/serial, selects and loads firmware, probes RSS slices/MSI-X, allocates coherent slice state, resets firmware, sets netdev features/queues/ethtool ops, tests IRQ allocation, saves PCI state, and registers the netdev. Open resets firmware, enables RSS, requests IRQs, sizes buffers, allocates rings, sets stats DMA and MTU/buffer sizes, enables Linux-style TSO, sends `ETHERNET_UP`, starts watchdog, and wakes TX queues. Close stops watchdog/NAPI/TX, sends `ETHERNET_DOWN`, waits for down IRQ, frees IRQs and rings.

State and persistence: host state includes ring indices, page/DMA mappings, per-slice counters, firmware stat blocks, command DMA memory, firmware name, EEPROM strings, link state, watchdog counters, and PCI saved state. Device state is in SRAM firmware, MCP rings, interrupt queues, and hardware link/PCI state. Firmware is reloaded or adopted at probe and watchdog recovery.

Dependencies and integration: uses PCI, DMA API, firmware loader, CRC32 validation, NAPI/GRO, ethtool, netdev queue APIs, MSI/MSI-X, VLAN helpers, GSO/TSO helpers, timers/workqueues, optional DCA, and MCP ABI headers.

Risks: bit/endian/DMA ABI is complex. TX segmentation must avoid crossing `tx_boundary`; fallback linearization is non-TSO only, while oversized IPv6 TSO may use software GSO. RX page reuse and unmap conditions are subtle. Firmware selection depends on PCIe alignment/ECRC tests. Watchdog recovery closes/reloads/reopens under RTNL and must avoid device-disappeared cases. A suspicious loop in watchdog recovery assigns `ss = mgp->ss` inside a per-slice loop, so review/test should confirm intended slice checking.

Test signals: firmware load CRC failure/adoption, EEPROM parsing, DMA benchmark, NAPI RX under small/jumbo/VLAN/GRO, TX checksum/TSO/GSO/fragments/boundary wrapping, MSI/MSI-X and RSS queue counts, ethtool stats/coalesce/pause/LED, multicast filtering including older firmware fallback, suspend/resume, watchdog reset recovery, and remove while interface is up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp.h

Purpose: host/firmware ABI definitions for Myri-10G MCP Ethernet firmware. It defines command, response, TX/RX descriptor, status block, firmware command IDs, error codes, flags, and limits used by `myri10ge.c`.

Important types: `mcp_dma_addr`, `mcp_slot`, `mcp_cmd`, `mcp_cmd_response`, `mcp_kreq_ether_send`, `mcp_kreq_ether_recv`, and `mcp_irq_data`. Important constants include firmware version `1.4`, send flags for checksum/TSO/small packets, SRAM command offsets, RSS commands, TSO mode commands, MDIO/I2C commands, and firmware error statuses.

Control flow: no code flow, but command enum values drive `myri10ge_send_cmd` interactions and firmware setup sequencing.

State and persistence: structs define shared memory and DMA-visible state exchanged with firmware. `mcp_irq_data` is persistently DMA-updated during interface runtime and holds link/drop/TX completion state.

Dependencies and integration: included by the Myricom driver; uses big-endian wire fields because firmware command descriptors are endian-defined.

Risks: ABI changes are high risk because firmware expects exact layouts and command numbers. Some flag values are intentionally overloaded for normal and TSO descriptors. `MXGEFW_OLD_IRQ_DATA_LEN` supports legacy stats DMA fallback.

Test signals: sparse/endian checks, firmware command coverage, descriptor layout validation, RSS/TSO/multicast command behavior, and ethtool stats derived from `mcp_irq_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp_gen_header.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp_gen_header.h

Purpose: generic MCP firmware header definitions used to validate loaded or running Myri-10G firmware and discover optional runtime metadata.

Important declarations: `MCP_HEADER_PTR_OFFSET`, MCP type constants (`MCP_TYPE_ETH`, `MCP_TYPE_PCIE`, etc.), `struct mcp_gen_header`, and `struct zmcp_info`. The header includes fixed leading fields and extension fields guarded by `header_length`.

Control flow: no executable flow. `myri10ge_load_hotplug_firmware`, `myri10ge_adopt_running_firmware`, and LED identification code read these structures from firmware image or NIC SRAM.

State and persistence: represents firmware image metadata and runtime SRAM metadata, including version string, SRAM size, string specs, MCP index, features, EEPROM header address, and LED patterns.

Dependencies and integration: included by `myri10ge.c`; relies on callers to swab/ntohl fields according to source location.

Risks: callers must check `header_length` before using extension fields. Incorrect header offset or type validation could load non-Ethernet firmware. LED support detection depends on `led_pattern` being within the advertised header length.

Test signals: firmware image validation with good/bad header offsets and types, adopted firmware validation, and ethtool physical ID LED behavior on firmware with and without LED fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp_gen_header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Kconfig

Purpose: Kconfig vendor menu for National Semiconductor Ethernet drivers, including SONIC variants and DP8381x/DP83820 PCI drivers.

Important symbols: `NET_VENDOR_NATSEMI` gates the menu. Driver symbols are `MACSONIC`, `MIPS_JAZZ_SONIC`, `NATSEMI`, `NS83820`, and `XTENSA_XT2000_SONIC`, each with platform or PCI dependencies. `NATSEMI` selects `CRC32`.

Control flow: configuration-only. Platform dependencies expose SONIC drivers only on relevant architectures/boards.

State and persistence: generated `.config` controls compilation and module availability.

Dependencies and integration: consumed by `natsemi/Makefile` and the wider Ethernet Kconfig hierarchy.

Risks: platform dependencies must stay accurate to avoid compiling drivers with unavailable arch headers. Help text references old external URLs but does not affect build.

Test signals: Kconfig builds for MIPS Jazz, Mac, Xtensa XT2000, and PCI configurations; verify unrelated architectures do not expose incompatible platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Makefile

Purpose: Kbuild mapping from NatSemi-related config symbols to driver objects.

Important declarations: maps `CONFIG_MACSONIC` to `macsonic.o`, `CONFIG_MIPS_JAZZ_SONIC` to `jazzsonic.o`, `CONFIG_NATSEMI` to `natsemi.o`, `CONFIG_NS83820` to `ns83820.o`, and `CONFIG_XTENSA_XT2000_SONIC` to `xtsonic.o`.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: paired with `natsemi/Kconfig`.

Risks: object names must match source files and config symbols. Multiple platform SONIC drivers share core code patterns, so build coverage should catch include/arch assumptions.

Test signals: per-symbol kernel builds and module packaging where the symbol is tristate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/jazzsonic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/jazzsonic.c

Purpose: platform driver for the onboard National Semiconductor SONIC Ethernet controller on MIPS Jazz systems. It provides Jazz-specific register access, probing, IRQ hookup, descriptor allocation/freeing, and delegates core SONIC operations to included `sonic.h`/`sonic.c`.

Important functions: `jazz_sonic_probe`, `sonic_probe1`, `jazzsonic_open`, `jazzsonic_close`, and `jazz_sonic_device_remove`. `sonic_netdev_ops` wires open/stop/start_xmit/get_stats/set_rx_mode/tx_timeout/address ops to wrapper or core SONIC functions. Register access macros `SONIC_READ` and `SONIC_WRITE` use volatile 32-bit MMIO via `dev->base_addr`.

Control flow: platform probe gets the memory resource, allocates an Ethernet device with `struct sonic_local`, stores device/driver data, assigns base address and IRQ, then calls `sonic_probe1`. `sonic_probe1` reserves the memory region, verifies a known silicon revision, resets the controller, reads the MAC address from CAM registers, sets 32-bit DMA mode, allocates descriptors, installs netdev ops, clears tally counters, and returns. Registering the netdev completes probe. Open requests the IRQ then calls `sonic_open`; close calls `sonic_close` then frees the IRQ.

State and persistence: netdev private `struct sonic_local` holds descriptor DMA state and device pointer. Descriptor memory is coherent DMA and freed on probe failure/remove. Hardware tally counters are cleared during probe; runtime state is managed by core SONIC code.

Dependencies and integration: depends on MIPS Jazz headers, Jazz DMA APIs, platform device resources, generic netdev/ethernet helpers, and included SONIC core implementation.

Risks: `#include "sonic.c"` makes compile-time coupling unusual but common for older platform variants. Probe assumes known revision `0x04`; unsupported but compatible revisions will be rejected. Direct volatile MMIO macros rely on correct register spacing. Error paths must release memory region and coherent descriptors exactly once.

Test signals: MIPS Jazz platform boot/probe, invalid revision rejection, MAC read correctness, IRQ open/close, packet TX/RX through core SONIC, multicast list updates, tx timeout handling, module/platform removal, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/jazzsonic.c -->
