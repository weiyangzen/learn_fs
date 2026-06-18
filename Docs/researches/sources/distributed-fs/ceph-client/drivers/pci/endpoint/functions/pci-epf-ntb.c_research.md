# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-ntb.c

## Purpose
Implements a PCI endpoint function that builds a non-transparent bridge from two endpoint controller interfaces. It exposes config, scratchpad, doorbell, and memory-window BARs to two hosts so each host can signal and map memory through the endpoint SoC.

## Important APIs, Types, And Functions
Core types are `struct epf_ntb`, `struct epf_ntb_epc`, and packed shared `struct epf_ntb_ctrl`. Important functions include `epf_ntb_bind()`, `epf_ntb_epc_create()`, `epf_ntb_init_epc_bar()`, `epf_ntb_config_spad_bar_alloc()`, `epf_ntb_epc_init_interface()`, `epf_ntb_cmd_handler()`, `epf_ntb_configure_db()`, `epf_ntb_configure_mw()`, `epf_ntb_link_up()`, and cleanup/free helpers. Configfs attributes expose `spad_count`, `db_count`, `num_mws`, and `mw1`-`mw4`.

## Control Flow
Probe allocates `epf_ntb` and installs ops. Bind waits until both primary and secondary EPCs are attached, creates per-interface state, chooses free BARs, allocates config/self-scratchpad memory, programs config/peer-scratchpad/doorbell/memory BARs, configures MSI/MSI-X, writes endpoint headers, and starts delayed command polling. Hosts write commands into shared control regions; the work handler configures or tears down doorbells and memory windows, and raises link events once both sides request link up.

## State And Persistence
Persistent state includes user-configured counts/sizes, per-interface EPC features, BAR assignments, BAR memory, peer outbound allocations, MSI-X table offsets, shared control registers, linkup flags, and delayed work. Shared control memory is host-visible and is the protocol state between host NTB drivers and this EPF.

## Dependencies And Integration Points
Depends on PCI endpoint core with primary and secondary EPC support, EPC BAR/MSI/MSI-X/address mapping APIs, configfs, and host-side NTB drivers that understand the control protocol.

## Risks
The command handler polls every 5 ms and has little synchronization around host-written control fields. BAR selection and sizing must satisfy both EPC feature sets. Cleanup loops use BAR ranges that need careful bounds. Doorbell mapping differs between MSI and MSI-X. Shared packed structures are ABI with host drivers.

## Test Signals
Instantiate via configfs with two EPCs, vary doorbell/scratchpad/MW sizes, validate MSI and MSI-X doorbells, memory-window map/unmap, peer scratchpad visibility, link-up/down commands from both hosts, bind waiting for the second EPC, unbind cleanup, and stress command polling during teardown.
