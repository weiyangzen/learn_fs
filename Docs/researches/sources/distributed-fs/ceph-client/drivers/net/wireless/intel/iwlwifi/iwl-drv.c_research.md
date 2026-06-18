# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.c

## Purpose
Implements the bus-agnostic iwlwifi driver core: firmware filename selection, asynchronous firmware request and fallback, firmware TLV parsing, firmware image allocation, debug TLV ingestion, opmode selection/start/stop, module parameters, and module init/exit around PCI registration.

## Important APIs, Types, and Functions
Main public APIs are `iwl_drv_start`, `iwl_drv_stop`, `iwl_opmode_register`, `iwl_opmode_deregister`, `iwl_drv_get_fwname_pre`, `iwl_drv_is_wifi7_supported`, and exported `iwlwifi_mod_params`. Important internals include `iwl_request_firmware`, `iwl_req_fw_callback`, `iwl_parse_v1_v2_firmware`, `iwl_parse_tlv_firmware`, `iwl_alloc_ucode`, `validate_sec_sizes`, `_iwl_op_mode_start`, `_iwl_op_mode_stop`, and firmware/debug cleanup helpers.

## Control Flow
`iwl_drv_start()` allocates `iwl_drv`, initializes debugfs/domains, and requests the newest supported firmware asynchronously. The callback parses legacy or TLV firmware, validates API/core range, copies firmware sections into VM allocations, imports debug TLVs and PNVM data, loads optional external debug TLVs, selects DVM/MVM/MLD opmode, starts it if registered, or requests its module. On firmware miss or incompatible image it decrements API and retries. Stop waits for callback completion, stops opmode, frees firmware/debug state, removes debugfs, and frees the driver.

## State and Persistence Behavior
Persistent runtime state lives in `struct iwl_drv`: parsed `iwl_fw`, opmode pointer, transport pointer, firmware index/name, completion, list node, and debugfs dentries. Firmware sections are copied from request-firmware buffers into owned VM memory. Module parameters persist globally and shape debug, restart, crypto, power, coexistence, and capability behavior.

## Dependencies and Integration Points
Depends on Linux firmware loader, module/debugfs/vmalloc/completion APIs, PCI registration (`iwl_pci_register_driver`), transport, opmode interface, config tables, firmware image/TLV ABIs, debug TLV framework, and MVM/DVM/MLD modules.

## Risks
The firmware callback is complex and asynchronous: failure paths must release firmware buffers, avoid double-freeing `pieces`, and unbind safely. TLV length validation is critical for untrusted firmware files. Opmode table locking protects start/stop/register races. Firmware API range and filename logic must match linux-firmware naming, including core-number encoding.

## Test Signals
Firmware load success, missing firmware fallback across API range, incompatible core/API rejection, malformed TLV lengths, old v1/v2 firmware, DVM section size validation, PNVM/debug TLV allocation, opmode absent then registered, opmode start retry on timeout, stop during firmware request, debugfs cleanup, module parameter parsing, and Wi-Fi 7 MLD selection are key.
