# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.h

## Purpose
Declares the public bus-agnostic iwlwifi driver interface, RF config bit extractors, export-symbol policy, KUnit visibility policy, init retry count, and firmware-prefix helper.

## Important APIs, Types, and Functions
Defines `DRV_NAME`, NVM and extended-NVM RF bitfield extractors, `iwl_drv_start`, `iwl_drv_stop`, `iwl_drv_is_wifi7_supported`, `IWL_EXPORT_SYMBOL`, `EXPORT_SYMBOL_IF_IWLWIFI_KUNIT`, `VISIBLE_IF_IWLWIFI_KUNIT`, `IWL_MAX_INIT_RETRY`, `FW_NAME_PRE_BUFSIZE`, and `iwl_drv_get_fwname_pre`.

## Control Flow
The header documents the high-level init flow from bus probe to async firmware fetch and opmode start. Runtime control flow is implemented in `iwl-drv.c`.

## State and Persistence Behavior
No state is stored here. The macros influence symbol visibility depending on modular opmode and KUnit configuration.

## Dependencies and Integration Points
Included by most iwlwifi modules. It bridges PCI/transport code to the common driver core and controls namespace exports for split opmode modules.

## Risks
RF bit extractors must match NVM layout. Export policy changes can break modular builds. `iwl_drv_start()` documentation says NULL on error, while implementation returns `ERR_PTR`, so callers must follow implementation behavior.

## Test Signals
Modular and built-in builds, KUnit builds, bus probe/remove calls, RF config parsing, firmware prefix helper users, and caller handling of `ERR_PTR` failures are relevant.
