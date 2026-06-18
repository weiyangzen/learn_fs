# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi.c

## Purpose

This is the auxiliary-bus glue driver for Intel Speed Select over TPMI. It binds VSEC-created `intel_vsec.tpmi-sst` devices to the shared TPMI SST core.

## Important APIs, Types, And Functions

`intel_sst_probe()` calls `tpmi_sst_init()` then `tpmi_sst_dev_add()`. `intel_sst_remove()` removes the device and decrements core usage. PM callbacks delegate to `tpmi_sst_dev_suspend()` and `tpmi_sst_dev_resume()`.

## Control Flow

The auxiliary driver registers through `module_auxiliary_driver()`. Probe initializes common TPMI char-device support once and adds the package/partition device. Remove reverses the device and core registration. Sleep PM saves/restores SST controls through the core.

## State And Persistence

This file stores no state itself. State lives in `isst_tpmi_core.c`.

## Dependencies And Integration Points

It imports `INTEL_TPMI_SST`, depends on Intel TPMI auxiliary enumeration, and connects device PM to the core.

## Risks

If `tpmi_sst_dev_add()` fails after core initialization, the probe explicitly calls `tpmi_sst_exit()`; mismatched usage counts would break later devices. All substantive behavior depends on the core's locking and package partition handling.

## Test Signals

Auxiliary device probe/remove, failure rollback, PM callback invocation, and module namespace imports validate this file.
