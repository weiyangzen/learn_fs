# subset-b-004390 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_main.c

## Purpose
Implements the PCI and `net_device` driver for the LiquidIO CN23xx virtual function. It probes VF PCI functions, initializes Octeon device state, negotiates PF/VF handshaking, creates the VF NIC interface, maps Linux transmit/receive operations to Octeon IQ/DROQ queues, and tears the device down on remove or fatal PCI error.

## Important APIs, Types, and Functions
Top-level integration is through `liquidio_vf_pci_driver`, `liquidio_vf_probe`, `liquidio_vf_remove`, `liquidio_vf_init`, and `liquidio_vf_exit`. Device bring-up is sequenced by `octeon_device_init`, which calls PCI setup, CN23xx VF register setup, dispatch setup, soft-command pool setup, IQ/DROQ setup, mailbox setup, MSI-X vector setup, PF/VF handshake, queue enable, initial OQ credits, and `liquidio_init_nic_module`. Netdev operations are collected in `lionetdevops`: open, stop, xmit, stats, MAC, multicast, VLAN filters, MTU, feature changes, and hardware timestamp get/set. Important helpers include `setup_nic_devices`, `send_rx_ctrl_cmd`, `lio_nic_info`, `update_link_status`, `liquidio_xmit`, `send_nic_timestamp_pkt`, and the SKB/gather cleanup callbacks.

## Control Flow
Probe allocates an `octeon_device`, stores it as PCI driver data, fills PCI identity fields, then runs the staged Octeon initialization. `setup_nic_devices` sends `OPCODE_NIC_IF_CFG` to firmware, receives queue masks, link info, MAC, and firmware version, allocates an Ethernet device, installs operations and ethtool hooks, sets offload features, creates IO queues and gather lists, registers the netdev, and enables default tunnel checksum features. Open enables NAPI, marks the interface running, starts TX queues, schedules stats work, and sends an RX start command. Stop sends RX stop, drops carrier, waits for RX drain, disables NAPI, re-enables the DROQ tasklet path, and cancels stats work. TX maps linear or SG SKB data for DMA, constructs Octeon command fields, handles checksum, VLAN, GSO, VXLAN, and TX timestamp flags, then sends a no-response or response soft command.

## State and Persistence Behavior
State is in `octeon_device` status bits, `oct->props[]`, queue masks, interrupt vectors, PF/VF handshake fields, and per-interface `struct lio` fields such as `ifstate`, `linfo`, `intf_open`, queue indices, feature capability masks, gather lists, and delayed work. Persistent external state is firmware-owned: link state, MAC permission, queue assignment, LRO/checksum/VXLAN/VLAN settings, RX forwarding state, and timestamps are communicated through Octeon commands. Removal uses the status machine in `octeon_destroy_resources` to unwind only the stages that were reached.

## Dependencies and Integration Points
Depends on Linux PCI, AER, MSI-X, netdevice, NAPI, VLAN, UDP tunnel, hardware timestamping, DMA mapping, and workqueue APIs. Driver-internal dependencies include `liquidio_common.h`, `octeon_droq.h`, `octeon_iq.h`, `response_manager.h`, `octeon_device.h`, `octeon_nic.h`, `octeon_network.h`, and `cn23xx_vf_device.h`. Firmware integration is through `OPCODE_NIC` soft commands and dispatch callbacks for `OPCODE_NIC_INFO`.

## Risks
The highest-risk code is lifecycle ordering: interrupts and queues are enabled before packets can arrive, and teardown must avoid freeing queues, IRQs, NAPI, tasklets, or soft commands while work is in flight. TX error paths can leak DMA mappings or gather-list entries if changed carelessly. `setup_nic_devices` has several partial-failure exits and relies on `caller_is_done` for soft-command ownership. Link-MTU changes run through a workqueue under RTNL. The AER path forcibly completes pending requests and disables PCI, so recovery behavior is intentionally limited for fatal errors.

## Test Signals
Useful signals include VF probe/remove, module load/unload, PF/VF handshake success, MSI-X vector allocation and affinity cleanup, netdev registration, interface up/down with RX start/stop commands, queue full and TX timeout behavior, linear and SG TX, TSO/TSO6, VLAN tag insertion and filtering, VXLAN tunnel port add/delete, RX checksum feature toggles, hardware TX/RX timestamping, link status updates including max-MTU reduction, AER nonfatal/fatal injection, and leak checks over failed init stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.c

## Purpose
Implements switchdev VF representor netdevices for LiquidIO PF mode. Each representor exposes a VF as a Linux netdev when the adapter is in switchdev eswitch mode, allowing control-plane operations and packet forwarding through firmware.

## Important APIs, Types, and Functions
The exported lifecycle functions are `lio_vf_rep_create`, `lio_vf_rep_destroy`, `lio_vf_rep_modinit`, and `lio_vf_rep_modexit`. Netdev operations are in `lio_vf_rep_ndev_ops`: `lio_vf_rep_open`, `lio_vf_rep_stop`, `lio_vf_rep_pkt_xmit`, `lio_vf_rep_tx_timeout`, `lio_vf_rep_phys_port_name`, `lio_vf_rep_get_stats64`, `lio_vf_rep_change_mtu`, and `lio_vf_get_port_parent_id`. Firmware commands are wrapped by `lio_vf_rep_send_soft_command` using `OPCODE_NIC_VF_REP_CMD`. Packet receive and transmit paths use `lio_vf_rep_pkt_recv`, `lio_vf_rep_copy_packet`, `lio_vf_rep_pkt_xmit`, and `lio_vf_rep_packet_sent_callback`.

## Control Flow
Creation first checks `DEVLINK_ESWITCH_MODE_SWITCHDEV` and SR-IOV enablement, then allocates one Ethernet device per VF, assigns an ifindex of `pf_num * 64 + vf + 1`, sets MTU bounds and netdev ops, registers the device, starts a delayed stats poll, and registers a dispatch handler for `OPCODE_NIC_VF_REP_PKT`. Open and stop send firmware state changes before toggling local carrier and queue state. TX validates the representor state, uses the parent PF netdev queue, maps the SKB linearly, prepares an `OPCODE_NIC_VF_REP_PKT` soft command with the representor ifidx, and frees the SKB in the callback. RX maps the firmware-provided ifidx from the response header to a representor netdev, copies or attaches page-backed data into the SKB, strips Octeon data header bytes, and injects it with `netif_rx`.

## State and Persistence Behavior
Per-representor state lives in `struct lio_vf_rep_desc`: parent netdev, representor netdev, Octeon device, stats snapshot, delayed work, atomic ifstate, and firmware ifidx. The Octeon device owns `vf_rep_list.ndev[]` and `num_vfs`. Firmware stores representor state, MTU, device name, and stats; the driver periodically refreshes stats and swaps TX/RX values when exposing them because a representor is a switch port.

## Dependencies and Integration Points
Depends on Linux netdevice notifier APIs, devlink eswitch mode, SR-IOV state, DMA mapping, SKB helpers, and LiquidIO soft-command, dispatch, network, and common ABI headers. It integrates with firmware through `lio_vf_rep_req` and `lio_vf_rep_resp`, and with the parent PF through `oct->props[0].netdev` and the parent's TX queue.

## Risks
The code supports only single-buffer representor packets on TX and rejects fragmented SKBs, so feature flags must not promise SG offload. The stats work reschedules itself unconditionally and must be cancelled before unregister/free. If dispatch registration fails after some netdevs were registered, cleanup must unwind all delayed work and devices. Ifidx arithmetic is tightly coupled to `CN23XX_MAX_VFS_PER_PF` and the firmware convention. Name sync rejects names longer than `LIO_IF_NAME_SIZE`, and soft-command ownership relies on `caller_is_done`.

## Test Signals
Test switchdev transition with SR-IOV enabled and disabled, representor create/destroy for multiple VFs, open/stop state commands, MTU changes, netdev rename sync, stats polling, representor TX/RX traffic, queue full and callback wakeup paths, fragmented SKB rejection, port-name strings like `pf0vf0`, parent-id reporting, and cleanup while stats work or firmware commands are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.h

## Purpose
Declares the small public interface and per-representor state used by LiquidIO VF representor support. It is the contract between `lio_vf_rep.c` and the rest of the PF driver.

## Important APIs, Types, and Functions
Constants include `LIO_VF_REP_REQ_TMO_MS` for command timeout intent and `LIO_VF_REP_STATS_POLL_TIME_MS` for periodic stats refresh. `struct lio_vf_rep_desc` stores parent and representor netdev pointers, the owning `octeon_device`, cached `lio_vf_rep_stats`, delayed stats work, atomic interface state, and firmware ifidx. `struct lio_vf_rep_sc_ctx` wraps a completion but is not used by the current C file. Public functions are `lio_vf_rep_create`, `lio_vf_rep_destroy`, `lio_vf_rep_modinit`, and `lio_vf_rep_modexit`.

## Control Flow
The header has no runtime control flow. Its declarations support module-level notifier registration, representor creation during switchdev/SR-IOV setup, and representor destruction during eswitch or device teardown.

## State and Persistence Behavior
The header defines in-memory state only. Persistent device-side representor attributes are defined in `liquidio_common.h` request/response structs and are synchronized by `lio_vf_rep.c`.

## Dependencies and Integration Points
It assumes definitions for `struct net_device`, `struct octeon_device`, `struct lio_vf_rep_stats`, `struct cavium_wk`, and `LIO_IFSTATE_RUNNING` are available through the including C file's header set. Its lifecycle functions are consumed by PF-side driver code that toggles switchdev representors.

## Risks
Because the header does not include all types it references, include order matters. The unused `lio_vf_rep_sc_ctx` is a maintenance signal. Timeout and polling constants must match firmware responsiveness and teardown expectations; an overly aggressive stats poll can amplify command latency or teardown races.

## Test Signals
Compile coverage with representor support built, switchdev enable/disable paths, stats-work cancellation, and include-order coverage from every C file that includes this header are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_common.h

## Purpose
Defines the host/firmware ABI shared across LiquidIO PF, VF, queue, network, console, and representor code. It contains protocol opcodes, command bit layouts, instruction and receive headers, link descriptors, interface configuration payloads, statistics layouts, capabilities, and VF representor request/response formats.

## Important APIs, Types, and Functions
Important constants include base driver version fields, `OPCODE_CORE`, `OPCODE_NIC`, `OPCODE_SUBCODE`, NIC subcodes such as `OPCODE_NIC_NW_DATA`, `OPCODE_NIC_CMD`, `OPCODE_NIC_IF_CFG`, `OPCODE_NIC_VF_REP_PKT`, and `OPCODE_NIC_VF_REP_CMD`, app modes, firmware capability flags, and NIC command IDs for MTU, MAC, RX control, multicast, LRO, checksum, VLAN, VXLAN, queue count, spoof check, and VF link state. Core types include `lio_version`, `octeon_sg_entry`, `union octnet_cmd`, `octeon_instr_ih3`, `octeon_instr_pki_ih3`, `octeon_instr_ih2`, `octeon_instr_irh`, `octeon_instr_rdp`, `union octeon_rh`, `union octnic_packet_params`, `union oct_link_status`, `oct_link_info`, `liquidio_if_cfg_info`, `nic_rx_stats`, `nic_tx_stats`, `oct_link_stats`, `oct_intrmod_cfg`, `union oct_nic_if_cfg`, and the VF-rep structures.

## Control Flow
The header has no standalone execution. It controls runtime branching through bitfields and helpers such as `incr_index`, `add_sg_size`, and `opcode_slow_path`. Queue code uses `opcode_slow_path` to decide whether a received packet is normal NIC data or should be dispatched to a registered opcode handler.

## State and Persistence Behavior
Most structs are serialized across PCI queues or firmware shared messages, so field widths, endian annotations, and bit ordering are persistent ABI. `oct_link_info` carries queue assignments, MAC, GMX port, link status, and spoof/admin flags. Stats structs are firmware snapshots. VF-rep request and response structs persist representor state changes, MTU, stats, and netdev names through firmware.

## Dependencies and Integration Points
Includes `octeon_config.h` and is included by most LiquidIO C files. It integrates Linux networking concepts with firmware protocol fields: checksum features, VLAN tags, hardware timestamps, LRO, VXLAN ports, link settings, and representor operations.

## Risks
This file is ABI-sensitive. Incorrect bitfield order, endian conversion, opcode values, struct sizes, or command constants can break host/firmware communication while compiling cleanly. Some fields are embedded in SKB control blocks or DMA command descriptors, so alignment and size changes have wide impact. `opcode_slow_path` depends on exact opcode/subcode composition.

## Test Signals
Compile on little- and big-endian bitfield configurations, firmware IF_CFG negotiation, NIC command round trips, RX/TX data paths, dispatch of non-data opcodes, link update parsing, stats fetches, VF-rep commands, timestamp packets, checksum/VLAN/VXLAN offload commands, and static checks for ABI struct sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_image.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_image.h

## Purpose
Defines the on-disk LiquidIO firmware image header consumed by the console firmware download path. It describes firmware naming conventions, image limits, boot command storage, and the network-byte-order file format for one or more binary images.

## Important APIs, Types, and Functions
Important constants are `LIO_FW_DIR`, `LIO_FW_BASE_NAME`, `LIO_FW_NAME_SUFFIX`, firmware type strings `nic`, `auto`, and `none`, maximum filename/type/version lengths, `LIO_MAX_BOOTCMD_LEN`, `LIO_MAX_IMAGES`, and `LIO_NIC_MAGIC`. `struct octeon_firmware_desc` stores big-endian load address, image length, and per-image CRC. `struct octeon_firmware_file_header` stores magic, version, boot command, image count, image descriptors, padding, and header CRC.

## Control Flow
There is no direct control flow. `octeon_download_firmware` in `octeon_console.c` reads this format, validates the magic, validates the header CRC, checks the version prefix against `LIQUIDIO_BASE_VERSION`, copies each image to the requested Octeon memory address, appends host UTC boot time to the boot command, and sends the command through the bootloader PCI console.

## State and Persistence Behavior
The header defines persistent firmware file layout. Numeric fields are network byte order, and the boot command is stored inside the firmware header then modified in memory before command submission. The firmware version string is copied into `oct->fw_info.liquidio_firmware_version`.

## Dependencies and Integration Points
Included by `octeon_console.c`. It depends on Linux fixed-endian integer types and CRC handling in the consumer. The constants align firmware file naming and loading behavior with host driver version negotiation in `liquidio_common.h`.

## Risks
The format is security- and reliability-sensitive because bad lengths or addresses could drive large PCI memory writes. The consumer validates header CRC and image count but does not validate a total file size for all image payloads in this header itself; callers must provide sane firmware data. Version prefix matching is strict to the base version string.

## Test Signals
Valid firmware load, invalid magic, bad header CRC, mismatched version, too many images, short file, long boot command after time append, multiple images, boundary chunk writes, and bootloader command failure are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_config.h

## Purpose
Defines static configuration limits and structs for LiquidIO Octeon devices, including maximum device counts, queue counts, descriptor sizes, default RX/TX ring parameters, interrupt coalescing defaults, NIC interface limits, BAR1 mapping constants, dispatch table sizing, and PF/VF maximums.

## Important APIs, Types, and Functions
Key macros define `MAX_OCTEON_NICIF`, `MAX_OCTEON_DEVICES`, `MAX_OCTEON_LINKS`, CN6xxx and CN23xx IQ/OQ limits and defaults, `CN23XX_MAX_VFS_PER_PF`, `CN23XX_MAX_RINGS_PER_VF`, `MAX_TXQS_PER_INTF`, `MAX_RXQS_PER_INTF`, `MAX_IOQS_PER_NICIF`, BAR1 mapping constants, response-list count, opcode mask sizing, and possible queue/VF maxima. Config accessor macros such as `CFG_GET_IQ_MAX_Q`, `CFG_GET_OQ_REFILL_THRESHOLD`, `CFG_GET_NUM_TX_DESCS_NIC_IF`, and `CFG_SET_NUM_RX_DESCS_NIC_IF` centralize field access. Types include `enum lio_card_type`, `octeon_iq_config`, `octeon_oq_config`, `octeon_nic_if_config`, `octeon_misc_config`, and `octeon_config`.

## Control Flow
There is no direct execution. Initialization code in `octeon_device.c`, queue setup, and chip-specific modules use these constants to size rings, choose defaults, allocate arrays, and validate queue identifiers. `MAX_OCTEON_INSTR_QUEUES(oct)` and `MAX_OCTEON_OUTPUT_QUEUES(oct)` drive loops across active queue arrays.

## State and Persistence Behavior
`struct octeon_config` instances are static in memory and copied or referenced by chip-specific setup. These values determine persistent runtime allocation sizes for DMA rings, pending lists, output buffers, refill thresholds, and interface queue layouts for the device lifetime.

## Dependencies and Integration Points
Consumed by `liquidio_common.h`, `octeon_device.c`, `octeon_droq.c`, IQ setup, chip-specific CN6xxx/CN23xx code, and SR-IOV/representor logic. Constants must align with firmware queue assignment and hardware ring capabilities.

## Risks
Changing descriptor counts, buffer sizes, queue maxima, or bitfield widths can break DMA ring sizing, memory consumption, interrupt moderation, and PF/VF resource partitioning. `MAX_OCTEON_*_QUEUES` currently keys CN23xx PF separately from other devices, so VF behavior inherits the CN6xxx-side limit in the macro even though other code uses CN23xx VF config explicitly.

## Test Signals
Probe on CN6xxx, CN23xx PF, and CN23xx VF, queue setup with default and boundary descriptor counts, SR-IOV VF allocation limits, representor ifidx mapping, BAR1 console mapping, interrupt coalescing defaults, and static checks that array maxima cover all configured queues and VFs are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_console.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_console.c

## Purpose
Implements host access to Octeon bootloader and PCI console memory, including named bootmem lookup, console polling, bootloader command submission, U-Boot version capture, and firmware image download/boot.

## Important APIs, Types, and Functions
Public functions are `octeon_console_send_cmd`, `octeon_wait_for_bootloader`, `octeon_init_consoles`, `octeon_add_console`, `octeon_remove_consoles`, and `octeon_download_firmware`. Internal structures mirror Octeon bootmem and console descriptors: `cvmx_bootmem_desc`, `octeon_pci_console`, and `octeon_pci_console_desc`. Important helpers include `__cvmx_bootmem_desc_get`, `CVMX_BOOTMEM_NAMED_GET_NAME`, `__cvmx_bootmem_check_version`, `cvmx_bootmem_phy_named_block_find`, `octeon_named_block_find`, `check_console`, `output_console_line`, `octeon_console_read`, and `octeon_get_uboot_version`.

## Control Flow
Console initialization verifies DDR memory access, finds the `__pci_console` named block, maps it through BAR1 static mapping, reads the number of consoles, and caches the descriptor address. Adding a console reads its ring buffer addresses and size, fetches U-Boot version by redirecting stdout to PCI, starts delayed polling, optionally enables debug console output, and marks it active. Polling reads available output bytes from a firmware ring buffer, advances the remote read index, prints complete lines while preserving leftovers, and reschedules itself. Firmware download validates the `liquidio_image.h` header, writes each image to Octeon memory in 4 MiB chunks, appends host UTC boot time to the boot command, and submits that command through the bootloader mailbox.

## State and Persistence Behavior
State is cached in `oct->bootmem_desc_addr`, `oct->bootmem_named_block_desc`, `oct->console_desc_addr`, `oct->num_consoles`, `oct->console[]`, and `oct->console_nb_info`. Console ring indices live in Octeon memory and are updated by host reads. Firmware version and boot command state are copied from the firmware header and then reflected in `oct->fw_info`.

## Dependencies and Integration Points
Depends on PCI core memory access helpers from `octeon_mem_ops.h`, indirect memory checks from `octeon_device.c`, BAR1 setup callbacks in `oct->fn_list`, CRC32, delayed work, and the firmware image layout from `liquidio_image.h`. It is used by PF firmware loading and diagnostics rather than the VF-only probe path.

## Risks
The remote lock functions are placeholders, so concurrent console or bootmem access is not serialized beyond caller behavior. Ring index validation prevents obvious out-of-range reads, but firmware-provided descriptor addresses and sizes are trusted after named block discovery. `octeon_download_firmware` validates the header but relies on the caller-provided `size` for the initial minimum only; image payload lengths should be covered by higher-level firmware loading tests. Polling uses a static console buffer shared by invocations.

## Test Signals
Bootloader readiness timeout, command length rejection, console named block missing, bootmem version mismatch, console ring wraparound, partial-line leftover printing, add/remove console with delayed work cancellation, U-Boot version capture, valid firmware boot, invalid firmware magic/CRC/version/image count, large image chunk writes, and boot command buffer overflow checks are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.c

## Purpose
Provides core Octeon device allocation, default configuration selection, global device registry, queue setup wrappers, dispatch table management, firmware core-ready handling, indirect PCI register access, memory readiness checks, and interrupt re-enable accounting for the LiquidIO driver family.

## Important APIs, Types, and Functions
Public entry points include `octeon_init_device_list`, `octeon_allocate_device`, `octeon_free_device_mem`, `octeon_register_device`, `octeon_deregister_device`, `octeon_allocate_ioq_vector`, `octeon_free_ioq_vector`, `octeon_setup_instr_queues`, `octeon_setup_output_queues`, `octeon_set_io_queues_off`, `octeon_set_droq_pkt_op`, `octeon_init_dispatch_list`, `octeon_delete_dispatch_list`, `octeon_get_dispatch`, `octeon_register_dispatch_fn`, `octeon_core_drv_init`, `octeon_get_tx_qsize`, `octeon_get_rx_qsize`, `octeon_get_conf`, `lio_get_device`, `lio_pci_readq`, `lio_pci_writeq`, `octeon_mem_access_ok`, `octeon_wait_for_ddr_init`, and `lio_enable_irq`.

## Control Flow
Device allocation reserves one contiguous block for `octeon_device`, private driver storage, chip-specific storage, and dispatch table entries, then inserts it into the global device array under lock. Registration shares adapter refcount and firmware state between functions on the same bus/device. Queue setup creates the initial IQ and OQ using chip-specific default descriptor counts and sizes. Dispatch initialization clears the hash table and request free-function table; registration installs the first opcode in-place and hash collisions on a linked list. Core-ready handling parses firmware app mode, capabilities, max ports, PKIND, board info, and moves the device to `OCT_DEV_CORE_OK`.

## State and Persistence Behavior
Static state includes default CN66xx, CN68xx, CN23xx configs, the global `octeon_device[]` table, adapter refcounts, adapter firmware states, and cached core setup. Per-device state includes PCI location, status, chip/config pointer, queue arrays, dispatch table, firmware info, board info, PF/VF handshake fields, and interrupt vectors. Register access functions serialize windowed BAR operations with `pci_win_lock`.

## Dependencies and Integration Points
Depends on Linux PCI/netdevice/vmalloc APIs and LiquidIO headers for IQ, DROQ, response management, network helpers, and chip-specific CN66xx/CN23xx definitions. It is called by PF and VF main drivers, DROQ processing, console memory checks, interrupt handlers, and netdev setup.

## Risks
Global device registry lifetime is delicate because lookup is lockless in `lio_get_device` while allocation/free update the array. Dispatch registration checks for duplicates outside the lock after releasing the first-level lock, so duplicate races would need external serialization. Queue setup initially creates only queue zero, with later NIC setup creating additional firmware-assigned queues. `octeon_set_io_queues_off` has chip-specific register paths and a shared loop counter for VF reset waits. Indirect PCI window reads/writes require strict ordering and locking.

## Test Signals
Multiple adapters and PF/VF functions, shared adapter refcounts, allocation failure paths, dispatch hash collisions and duplicate registration, firmware core-ready packet parsing, queue size queries, CN23xx VF IO queue reset clearing, DDR-ready timeout, indirect CSR reads/writes, IRQ resend behavior for IQ and DROQ, and teardown after partial initialization are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.h

## Purpose
Defines the central LiquidIO Octeon device model, device states, PCI IDs, interrupt bits, BAR/window mappings, dispatch table structures, console caches, chip callback table, board and firmware metadata, SR-IOV bookkeeping, MSI-X vector records, devlink/switchdev state, and public core-device APIs.

## Important APIs, Types, and Functions
Important enums and constants include Octeon PCI IDs, CN23xx revisions and subsystem IDs, PCI swap modes, firmware load states, Octeon device states from `OCT_DEV_BEGIN_STATE` through `OCT_DEV_IN_RESET`, interrupt masks, BAR1 mapping flags, and private ethtool flags. Important structs are `octeon_dispatch`, `octeon_dispatch_list`, `octeon_mmio`, `octeon_reg_list`, `octeon_console`, `octeon_board_info`, `octeon_fn_list`, `cvmx_bootmem_named_block_desc`, `oct_fw_info`, `cavium_wk`, `cavium_wq`, `octdev_props`, `octeon_pf_vf_hs_word`, `octeon_sriov_info`, `octeon_ioq_vector`, `lio_vf_rep_list`, `lio_devlink_priv`, and the large `octeon_device`.

## Control Flow
The header has no runtime flow, but its status constants define the staged initialization and teardown switch used by main drivers. Function pointers in `octeon_fn_list` allow chip-specific code to provide register setup, mailbox, reset, BAR1, queue, and interrupt operations while common code drives the sequence.

## State and Persistence Behavior
`struct octeon_device` is the long-lived root object for one PCI function. It persists queue pointers, queue masks, response lists, dispatch entries, console addresses, firmware info, board info, SR-IOV settings, VF MAC/VLAN/link/spoof state, mailbox pointers, link stats, devlink mode, and coalescing settings for the device lifetime.

## Dependencies and Integration Points
Includes Linux interrupt and devlink headers. It is consumed across the LiquidIO driver: PF/VF main, device core, IQ/DROQ, console, ethtool, network, mailbox, SR-IOV, and representor code. It links chip-specific implementations to common code through `octeon_fn_list`.

## Risks
This header is high-blast-radius. Any size or semantic change to `octeon_device`, status constants, queue maxima, or callback contracts affects initialization, interrupt handling, netdev setup, and teardown. Several arrays are sized by maximum possible queues or VFs, so mismatches with `octeon_config.h` can cause out-of-bounds use or inaccessible queues. Locking expectations are encoded but not enforced by types.

## Test Signals
Full build coverage for PF and VF, staged init/teardown, SR-IOV enable/disable, devlink switchdev representors, mailbox setup/free, console initialization, interrupt vector setup, queue allocation, ethtool private flags, and static analysis for array bounds and callback null checks are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.c

## Purpose
Implements Descriptor Ring Output Queues, which are Octeon-to-host receive queues. It allocates DMA descriptor rings and receive buffers, tracks hardware packet counts, converts completed descriptors into SKBs or dispatch packets, refills descriptors, handles low-credit/OOM recovery, and registers per-queue receive operations.

## Important APIs, Types, and Functions
Public functions include `octeon_get_dispatch_arg`, `octeon_droq_check_hw_for_pkts`, `octeon_delete_droq`, `octeon_init_droq`, `octeon_retry_droq_refill`, `octeon_droq_process_packets`, `octeon_droq_process_poll_pkts`, `octeon_enable_irq`, `octeon_register_droq_ops`, `octeon_unregister_droq_ops`, and `octeon_create_droq`. Internal helpers include `octeon_droq_setup_ring_buffers`, `octeon_droq_destroy_ring_buffers`, `octeon_create_recv_info`, `octeon_droq_refill`, `octeon_droq_dispatch_pkt`, `octeon_droq_drop_packets`, and `octeon_droq_fast_process_packets`.

## Control Flow
Initialization allocates a coherent descriptor ring, allocates one receive buffer per descriptor, maps buffers for device DMA, computes the maximum safe empty descriptor threshold for 64 KiB packets, initializes dispatch list state, and asks chip code to program OQ registers. Runtime processing reads the hardware packet count, caps work by budget, swaps descriptor metadata, distinguishes normal NIC data from slow-path opcodes, either passes packets to `droq->ops.fptr` or queues dispatch callbacks, advances read/refill indices, refills descriptors when thresholds are reached, writes credits after a memory barrier, then runs queued dispatch functions. Poll-mode processing loops until budget is consumed or no packets remain.

## State and Persistence Behavior
Persistent queue state is in `struct octeon_droq`: descriptor DMA address, ring indices, pending packet count, refill count, thresholds, receive buffer list, credit/sent registers, dispatch list, stats, NAPI object, app context, and CPU callback data. Buffers transition from device-owned DMA mappings to host-owned SKBs/pages and back during refill.

## Dependencies and Integration Points
Depends on DMA helpers, page/SKB receive-buffer helpers from `octeon_network.h`, dispatch registration from `octeon_device.c`, IQ interrupt accounting, chip-specific register setup, NAPI/tasklet callers, and LiquidIO firmware receive headers from `liquidio_common.h`.

## Risks
Ring index, refill, and DMA ownership bugs can corrupt receive traffic or leak pages. Multi-buffer packet assembly and slow-path dispatch depend on accurate firmware length and header fields. Low-memory behavior tries to pull up undispatched buffers and schedule OOM recovery; regressions can starve the device of credits. `octeon_create_droq` increments `num_oqs` after `octeon_init_droq`, while `octeon_init_droq` is also used by initial setup that increments elsewhere, so call-site ownership matters.

## Test Signals
RX traffic with linear and jumbo packets, slow-path dispatch packets, no-dispatch drops, low-memory refill failure, OOM retry, NAPI and tasklet processing, budget limits with `drop_on_max`, queue delete after packets, interrupt resend/enable, descriptor credit accounting, page recycling, DMA unmap checks, and stats counters are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.h

## Purpose
Declares the Descriptor Ring Output Queue data model and public receive-queue APIs. In LiquidIO terminology output is from the Octeon device, so these structures implement host ingress.

## Important APIs, Types, and Functions
Important structs include `octeon_droq_desc` for DMA buffer/info pointers, `octeon_droq_info` for packet length and receive header, `octeon_skb_page_info` for page DMA ownership, `octeon_recv_buffer`, `oct_droq_stats`, `octeon_recv_pkt`, `octeon_recv_info`, `octeon_droq_ops`, and `octeon_droq`. Inline helpers allocate and free `octeon_recv_info`. Public prototypes cover DROQ init/delete/create, packet processing in tasklet and poll mode, interrupt enable, refill retry, dispatch registration, and dispatch argument lookup.

## Control Flow
The header has no direct runtime flow, but its callback structure controls whether the C implementation sends normal packets to a queue-specific fast-path function or falls back to opcode dispatch. `poll_mode` and `drop_on_max` influence receive processing behavior under NAPI and budget pressure.

## State and Persistence Behavior
`octeon_droq` persists all ring and buffer state for a receive queue: descriptor ring, read/write/refill indices, packet counters, thresholds, receive buffer list, hardware credit/sent register mappings, dispatch list, stats, DMA address, app context, and NAPI metadata. `octeon_recv_pkt` and `octeon_recv_info` are transient dispatch containers.

## Dependencies and Integration Points
Depends on `union octeon_rh` from `liquidio_common.h`, Linux NAPI and page/DMA concepts, and `octeon_device` ownership. It is consumed by core device setup, VF/PF netdev receive setup, interrupt handlers, and representor receive dispatch.

## Risks
Struct layout and queue state fields are tightly coupled to DMA descriptor programming and packet processing. `MAX_RECV_BUFS` assumes a 64 KiB maximum packet and typical buffer sizing; changing buffer sizes or max packet sizes requires revisiting this bound. Callback ownership rules must be clear because buffers passed through `fptr` or dispatch functions are no longer refill-owned.

## Test Signals
Build coverage, descriptor size checks, receive queue init/delete, NAPI poll and tasklet processing, dispatch function registration, stats updates, jumbo receive buffer counts, low-credit refill, and callback buffer ownership tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.h -->
