# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smumgr.c

## Purpose
This file is the generic SMU manager dispatch layer for the legacy AMD PowerPlay stack. It declares firmware blobs required by supported ASICs and provides stable wrapper functions that call the currently selected `hwmgr->smumgr_funcs` implementation.

## Important APIs, types, and functions
The `MODULE_FIRMWARE` declarations cover SMU firmware for Bonaire, Hawaii, Topaz, Tonga, Fiji, Polaris10/11/12, VegaM, Vega10, Vega12, and Vega20 variants. Wrapper APIs include thermal/AVFS setup, SCLK threshold update, SMU table update, firmware-header processing, macro/offset lookup, PowerPlay table download/upload, message sending with optional response capture, SMC table management, DPM-running and AVFS-present checks, MC register table initialization, profile update, and SMU stop.

## Control flow
Most wrappers are null-safe dispatch functions: if the selected backend provides the callback, the wrapper calls it; otherwise it returns a neutral default such as 0, true, false, or `-EINVAL` depending on the API. `smum_send_msg_to_smc` and `smum_send_msg_to_smc_with_parameter` validate required callbacks, serialize mailbox access with `hwmgr->msg_lock`, invoke the backend send function, optionally fetch the argument, and release the mutex.

## State, dependencies, risks, and test signals
This file owns no backend state. Its persistent effect is through function dispatch into the active SMU manager and through the message mutex protecting firmware mailbox registers shared across the driver. It is the integration point used by hwmgr, powertune, clock/power gating, display, and ASIC-specific code. Neutral defaults can hide missing backend functionality, and several backends return 0 after logging firmware errors. Test signals include correct backend selection, successful firmware blob requests, no concurrent mailbox corruption, expected `-EINVAL` when a required callback is absent, and meaningful response values when callers request `resp`.
